"""
Evoked response detection - Processing functions
=====================================================


Copyright 2023, Max van den Boom (Multimodal Neuroimaging Lab, Mayo Clinic, Rochester MN)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import os
import datetime
import logging
from math import isnan, ceil
import numpy as np
import scipy.io as sio
from os.path import exists

from ieegprep.bids.sidecars import load_channel_info, load_elec_stim_events, load_ieeg_sidecar
from ieegprep.bids.data_epoch import load_data_epochs_averages
from ieegprep.bids.rereferencing import RerefStruct
from ieegprep.utils.console import multi_line_list, print_progressbar
from ieegprep.utils.misc import is_number

from erdetect.version import __version__
from erdetect.core.config import write_config, get as cfg, get_config_dict, OUTPUT_IMAGE_SIZE, LOGGING_CAPTION_INDENT_LENGTH
from erdetect.core.detection import ieeg_detect_er
from erdetect.views.output_images import calc_sizes_and_fonts, calc_matrix_image_size, gen_amplitude_matrix, gen_latency_matrix
from erdetect.utils.misc import create_figure
from erdetect.core.metrics.metric_cross_proj import MetricCrossProj
from erdetect.core.metrics.metric_waveform import MetricWaveform


def process_subset(bids_subset_data_path, output_dir, preproc_prioritize_speed=False):
    """
    Process a BIDS subset, perform pre-processing, evoked response detection and produce output

    Args:
        bids_subset_data_path (str):          The path to the data of a subset (e.g. /BIDS/sub-01/ses-ieeg01/ieeg/sub-01_task-ccep.mefd)
                                              Paths other required files such as the _channels.tsv and _events.tsv file
                                              will be derived from the data path.
        output_dir (str):                     The path to store the output files in. A subdirectory will be created for each subset.
        preproc_prioritize_speed (bool):      Set the pre-processing priority to either memory (default, False) or speed (True).

    """

    # check the input arguments
    if not bids_subset_data_path:
        logging.error('Empty or invalid input data path, make sure to provide a path to subset data (e.g. \'/bids_data_root/subj-01/ieeg/sub-01_run-06.edf\'), exiting...')
        return

    bids_subset_data_path = os.path.abspath(os.path.expanduser(os.path.expandvars(bids_subset_data_path)))
    if not exists(bids_subset_data_path):
        logging.error('Input data path (\'' + bids_subset_data_path + '\') could not be found.\nMake sure to provide a path to subset data (e.g. \'/bids_data_root/subj-01/ieeg/sub-01_run-06.edf\'), exiting...')
        return

    if not output_dir:
        logging.error('Empty or invalid output directory, exiting...')
        return
    output_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(output_dir)))

    # derive the bids subset root from the full path
    try:
        bids_subset_root = bids_subset_data_path[:bids_subset_data_path.rindex('_')]
    except ValueError:
        logging.error('Invalid input data path, make sure to provide a path to subset data (e.g. \'/bids_data_root/subj-01/ieeg/sub-01_run-06.edf\'), exiting...')
        return

    # determine a subset specific output path
    output_root = os.path.join(output_dir, os.path.basename(os.path.normpath(bids_subset_root)))

    # make sure the subject output directory exists
    if not os.path.exists(output_root):
        try:
            os.makedirs(output_root)
        except OSError as e:
            logging.error("Could not create subset output directory (\'" + output_root + "\'), exiting...")
            raise RuntimeError('Could not create subset output directory')

    #
    # logging
    #

    #
    subset_log_filepath = os.path.join(output_root, 'subset__' + datetime.datetime.now().strftime("%Y%m%d__%H%M%S") + '.log')

    # write the application header and configuration information to a subset specific logfile
    set_text = []
    set_text.append('------------------------ Evoked Response Detection - v' + __version__ + ' ------------------------')
    set_text.append('')
    log_config(preproc_prioritize_speed, set_text)
    with open(subset_log_filepath, 'w') as f:
        for line in set_text:
            f.write(line + '\n')

    #
    root_logger = logging.getLogger()
    subset_logger_file = logging.FileHandler(subset_log_filepath, mode='a')
    subset_logger_file.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(subset_logger_file)

    # print subset information
    logging.info('------------------------ Processing subset ------------------------')
    log_single_line('Subset input:', bids_subset_root + '*.*')
    log_single_line('Subset output path:', output_root + os.path.sep)
    logging.info('')


    #
    # Line noise removal and IEEG JSON sidecar
    #
    line_noise_removal = None
    if str(cfg('preprocess', 'line_noise_removal')).lower() == 'json':
        try:
            ieeg_json = load_ieeg_sidecar(bids_subset_root + '_ieeg.json')

            # check if the field exists
            if 'PowerLineFrequency' not in ieeg_json:
                logging.error('Could not find the \'PowerLineFrequency\' field in the IEEG JSON sidecar (\'' + bids_subset_root + '_ieeg.json\') this is required to perform line-noise removal, exiting...')
                raise RuntimeError('Could not find field in the IEEG JSON sidecar')

            # check if the field is a number and higher than 0
            if not is_number(ieeg_json['PowerLineFrequency']) or ieeg_json['PowerLineFrequency'] <= 0:
                logging.error('Invalid value for the \'PowerLineFrequency\' field in the IEEG JSON sidecar (\'' + bids_subset_root + '_ieeg.json\'), positive integer is required to perform line-noise removal, exiting...')
                raise RuntimeError('Invalid value in the IEEG JSON sidecar')

            # use the PowerLineFrequency value
            line_noise_removal = float(ieeg_json['PowerLineFrequency'])
            log_single_line('Powerline frequency from IEEG JSON sidecar:', str(line_noise_removal))

        except (IOError, RuntimeError):
            logging.error('Could not load the IEEG JSON sidecar (\'' + bids_subset_root + '_ieeg.json\') that is required to perform line-noise removal, exiting...')
            raise RuntimeError('Could not load the IEEG JSON sidecar')

    else:
        # not from JSON

        # check if there is a number in the config, if so, use it
        if not cfg('preprocess', 'line_noise_removal').lower() == 'off':
            line_noise_removal = float(cfg('preprocess', 'line_noise_removal'))


    #
    # retrieve channel metadata
    #

    # retrieve the channel metadata from the channels.tsv file
    try:
        channel_tsv = load_channel_info(bids_subset_root + '_channels.tsv')
    except (FileNotFoundError, LookupError):
        logging.error('Could not load the channel metadata (\'' + bids_subset_root + '_channels.tsv\'), exiting...')
        raise RuntimeError('Could not load the channel metadata')

    # sort out the good, the bad and the... non-ieeg
    channels_excl_bad = []                                  # channels excluded because they are marked as bad
    channels_incl = []                                      # channels that need to be loaded (either to be used as measured electrode or for re-referencing)

    channels_measured_incl = []                             # the channels that are used as measured electrodes
    channels_stim_incl = []                                 # the channels which stim-pairs should be included (actual filtering of stim-pairs happens at the reading of the events)
    channels_early_reref_incl_names = []                    # the names of the channels that are included for early re-referencing
    channels_early_reref_incl_headbox = []                  # the headbox that each of the included early re-referencing channels belong to
    channels_late_reref_incl_names = []                     # the names of the channels that are included for late re-referencing
    channels_late_reref_incl_headbox = []                   # the headbox that each of the included late re-referencing channels belong to

    channels_measured_excl_by_type = []                     # channels that were excluded as measured electrodes (by type)
    channels_stim_excl_by_type = []                         # channels that were excluded (and as a result exclude stim-pairs)
    channels_early_reref_excl_by_type = []                  #
    channels_late_reref_excl_by_type = []                  #

    channels_have_status = 'status' in channel_tsv.columns
    channels_have_headbox = 'headbox' in channel_tsv.columns
    for index, row in channel_tsv.iterrows():

        # check if bad channel
        if channels_have_status and row['status'].lower() == 'bad':
            channels_excl_bad.append(row['name'])

            # continue to the next channel
            continue

        # determine if included or excluded from measured electrodes (by type)
        if row['type'].upper() in cfg('channels', 'measured_types'):

            channels_measured_incl.append(row['name'])          # save for log output and plotting
            channels_incl.append(row['name'])                   # save for data reading

        else:
            channels_measured_excl_by_type.append(row['name'])  # save for log output

        # determine if included or excluded from stimulated electrodes (by type)
        if row['type'].upper() in cfg('channels', 'stim_types'):
            channels_stim_incl.append(row['name'])              # save for log output and stim-pair event selection
        else:
            channels_stim_excl_by_type.append(row['name'])      # save for log output and stim-pair event selection

        # determine if included or excluded from early re-referencing electrodes (by type)
        if cfg('preprocess', 'early_re_referencing', 'enabled'):
            if row['type'].upper() in cfg('preprocess', 'early_re_referencing', 'channel_types'):

                # save for log output and the early-referencing (structure)
                channels_early_reref_incl_names.append(row['name'])
                if channels_have_headbox:
                    channels_early_reref_incl_headbox.append(row['headbox'])

                # save for data reading (no duplicates)
                if not row['name'] in channels_incl:
                    channels_incl.append(row['name'])

            else:
                channels_early_reref_excl_by_type.append(row['name'])   # save for log output

        # determine if included or excluded from late re-referencing electrodes (by type)
        if cfg('preprocess', 'late_re_referencing', 'enabled'):
            if row['type'].upper() in cfg('preprocess', 'late_re_referencing', 'channel_types'):

                # save for log output and the late-referencing (structure)
                channels_late_reref_incl_names.append(row['name'])
                if channels_have_headbox:
                    channels_late_reref_incl_headbox.append(row['headbox'])
                    # TODO: what if nan or not a number

                # save for data reading (no duplicates)
                if not row['name'] in channels_incl:
                    channels_incl.append(row['name'])

            else:
                channels_late_reref_excl_by_type.append(row['name'])   # save for log output

    # print channel information
    logging.info(multi_line_list(channels_excl_bad, LOGGING_CAPTION_INDENT_LENGTH, 'Bad channels (excluded):', 14, ' '))
    if channels_measured_excl_by_type == channels_stim_excl_by_type:
        logging.info(multi_line_list(channels_measured_excl_by_type, LOGGING_CAPTION_INDENT_LENGTH, 'Channels excluded by type:', 14, ' '))
    else:
        logging.info(multi_line_list(channels_measured_excl_by_type, LOGGING_CAPTION_INDENT_LENGTH, 'Channels excl. (by type) as measured electrodes:', 14, ' '))
        logging.info(multi_line_list(channels_stim_excl_by_type, LOGGING_CAPTION_INDENT_LENGTH, 'Channels excl. (by type) as stim electrodes:', 14, ' '))
    logging.info('')
    if channels_measured_incl == channels_stim_incl:
        logging.info(multi_line_list(channels_measured_incl, LOGGING_CAPTION_INDENT_LENGTH, 'Channels included as electrodes:', 14, ' ', str(len(channels_measured_incl))))
    else:
        logging.info(multi_line_list(channels_measured_incl, LOGGING_CAPTION_INDENT_LENGTH, 'Channels incl. as measured electrodes:', 14, ' ', str(len(channels_measured_incl))))
        logging.info(multi_line_list(channels_stim_incl, LOGGING_CAPTION_INDENT_LENGTH, 'Channels incl. as stim electrodes:', 14, ' ', str(len(channels_stim_incl))))


    # check if there are any channels (as measured electrodes, or to re-reference on)
    if len(channels_measured_incl) == 0:
        logging.error('No channels were found (after filtering by type), exiting...')
        raise RuntimeError('No channels were found')

    # check early re-referencing settings and prepare reref struct
    early_reref = None
    if cfg('preprocess', 'early_re_referencing', 'enabled'):

        if cfg('preprocess', 'early_re_referencing', 'method') == 'CAR_headbox' and not channels_have_headbox:
            logging.error('Early re-referencing is set to CAR per headbox, but the _channels.tsv file does not have a \'headbox\' column, exiting...')
            raise RuntimeError('No \'headbox\' column in _channels.tsv file, needed to perform early re-referencing per headbox')

        if len(channels_early_reref_incl_names) == 0:
            logging.info(multi_line_list(channels_early_reref_incl_names, LOGGING_CAPTION_INDENT_LENGTH, 'Channels included (by type) for early re-ref:', 14, ' '))
            logging.info(multi_line_list(channels_early_reref_excl_by_type, LOGGING_CAPTION_INDENT_LENGTH, 'Channels excluded by type for early re-ref:', 14, ' '))
            logging.error('Early re-referencing is enabled but (after filtering by type) no channels were found, exiting...')
            raise RuntimeError('No channels were found for early re-referencing')

        # generate an early re-referencing object
        if cfg('preprocess', 'early_re_referencing', 'method') == 'CAR':
            early_reref = RerefStruct.generate_car(channels_early_reref_incl_names)
        elif cfg('preprocess', 'early_re_referencing', 'method') == 'CAR_headbox':
            early_reref = RerefStruct.generate_car_per_headbox(channels_early_reref_incl_names, channels_early_reref_incl_headbox)

            # print CAR headbox info
            logging.info('')
            log_single_line('Early re-referencing groups:', '')
            for ind, group in enumerate(early_reref.groups):
                logging.info(multi_line_list(group, LOGGING_CAPTION_INDENT_LENGTH, '      CAR group ' + str(ind) + ':', 14, ' '))

            # check to make sure all included channels are also included in early re-referencing
            missing_channels = []
            for channel in channels_measured_incl:
                if channel not in early_reref.channel_group.keys():
                    missing_channels.append(channel)
            if len(missing_channels) == 1:
                logging.error('Channel \'' + missing_channels[0] + '\' is included but cannot be found in any early re-referencing group, make sure the channel has a valid headbox value in the _channels.tsv')
                raise RuntimeError('Included channel not in re-referencing group')
            elif len(missing_channels) > 1:
                logging.error('Channels \'' + ', '.join(missing_channels) + '\' are included but cannot be found in any early re-referencing group, make sure the channels have valid headbox values in the _channels.tsv')
                raise RuntimeError('Included channel not in re-referencing group')


    # check late re-referencing settings and prepare reref struct
    late_reref = None
    if cfg('preprocess', 'late_re_referencing', 'enabled'):

        if cfg('preprocess', 'late_re_referencing', 'method') == 'CAR_headbox' and not channels_have_headbox:
            logging.error('Late re-referencing is set to CAR per headbox, but the _channels.tsv file does not have a \'headbox\' column, exiting...')
            raise RuntimeError('No \'headbox\' column in _channels.tsv file, needed to perform late re-referencing per headbox')

        if len(channels_late_reref_incl_names) == 0:
            logging.info(multi_line_list(channels_late_reref_incl_names, LOGGING_CAPTION_INDENT_LENGTH, 'Channels included (by type) for late re-ref:', 14, ' '))
            logging.info(multi_line_list(channels_late_reref_excl_by_type, LOGGING_CAPTION_INDENT_LENGTH, 'Channels excluded by type for late re-ref:', 14, ' '))
            logging.error('Late re-referencing is enabled but (after filtering by type) no channels were found, exiting...')
            raise RuntimeError('No channels were found for late re-referencing')

        # generate a late re-referencing object
        if cfg('preprocess', 'late_re_referencing', 'method') == 'CAR':
            late_reref = RerefStruct.generate_car(channels_late_reref_incl_names)
            if cfg('preprocess', 'late_re_referencing', 'CAR_by_variance') != -1:
                late_reref.late_group_reselect_varPerc = cfg('preprocess', 'late_re_referencing', 'CAR_by_variance')

        elif cfg('preprocess', 'late_re_referencing', 'method') == 'CAR_headbox':
            late_reref = RerefStruct.generate_car_per_headbox(channels_late_reref_incl_names, channels_late_reref_incl_headbox)
            if cfg('preprocess', 'late_re_referencing', 'CAR_by_variance') != -1:
                late_reref.late_group_reselect_varPerc = cfg('preprocess', 'late_re_referencing', 'CAR_by_variance')

            # print CAR headbox info
            logging.info('')
            log_single_line('Late re-referencing groups:', '')
            for ind, group in enumerate(late_reref.groups):
                logging.info(multi_line_list(group, LOGGING_CAPTION_INDENT_LENGTH, '      CAR group ' + str(ind) + ':', 14, ' '))

            # check to make sure all included channels are also included in late re-referencing
            missing_channels = []
            for channel in channels_measured_incl:
                if channel not in late_reref.channel_group.keys():
                    missing_channels.append(channel)
            if len(missing_channels) == 1:
                logging.error('Channel \'' + missing_channels[0] + '\' is included but cannot be found in any late re-referencing group, make sure the channel has a valid headbox value in the _channels.tsv')
                raise RuntimeError('Included channel not in re-referencing group')
            elif len(missing_channels) > 1:
                logging.error('Channels \'' + ', '.join(missing_channels) + '\' are included but cannot be found in any late re-referencing group, make sure the channels have valid headbox values in the _channels.tsv')
                raise RuntimeError('Included channel not in re-referencing group')

    logging.info('')


    #
    # retrieve trials (onsets) and stim-pairs conditions
    #

    # retrieve the electrical stimulation events (onsets and stim-pairs) from the events.tsv file
    # only retrieve the stim-pairs for the channels that are included
    try:
        trial_onsets, trial_pairs, stim_pairs_onsets, bad_trial_onsets = load_elec_stim_events(bids_subset_root + '_events.tsv',
                                                                                             exclude_bad_events=True,
                                                                                             concat_bidirectional_stimpairs=cfg('trials', 'concat_bidirectional_pairs'),
                                                                                             only_stimpairs_between_channels=channels_stim_incl)
    except (RuntimeError):
        logging.error('Could not load the electrical stimulation event metadata (\'' + bids_subset_root + '_events.tsv\'), exiting...')
        raise RuntimeError('Could not load the electrical stimulation event metadata')

    if len(bad_trial_onsets) > 0:
        log_single_line('Number of trials marked as bad (excluded):', str(len(bad_trial_onsets)))

    # check if there are trials
    if len(trial_onsets) == 0:
        logging.error('No trials were found, exiting...')
        raise RuntimeError('No trials found')

    # determine the stimulus-pairs conditions that have too little trials
    stimpair_remove_keys = []
    for stim_pair, onsets in stim_pairs_onsets.items():
        if len(onsets) < cfg('trials', 'minimum_stimpair_trials'):
            stimpair_remove_keys.append(stim_pair)

    # remove the stimulus-pairs with too little trials
    if len(stimpair_remove_keys) > 0:

        # message
        stimpair_print = [stim_pair + ' (' + str(len(stim_pairs_onsets[stim_pair])) + ' trials)' for stim_pair in stimpair_remove_keys]
        stimpair_print = [str_print.ljust(len(max(stimpair_print, key=len)), ' ') for str_print in stimpair_print]
        logging.info(multi_line_list(stimpair_print, LOGGING_CAPTION_INDENT_LENGTH, 'Stim-pairs excluded by number of trials:', 3, '   '))

        # remove those stimulation-pairs
        for stim_pair in stimpair_remove_keys:
            del stim_pairs_onsets[stim_pair]

    # display stimulation-pair/trial information
    stimpair_print = [stim_pair + ' (' + str(len(onsets)) + ' trials)' for stim_pair, onsets in stim_pairs_onsets.items()]
    stimpair_print = [str_print.ljust(len(max(stimpair_print, key=len)), ' ') for str_print in stimpair_print]
    logging.info(multi_line_list(stimpair_print, LOGGING_CAPTION_INDENT_LENGTH, 'Stimulation pairs included:', 3, '   ', str(len(stim_pairs_onsets))))

    # check if there are stimulus-pairs
    if len(stim_pairs_onsets) == 0:
        logging.error('No stimulus-pairs were found, exiting...')
        raise RuntimeError('No stimulus-pairs found')

    # set the parts of stimulation (of specific channels) to exclude from early or late re-referencing
    if early_reref is not None:
        early_reref.set_exclude_reref_epochs(stim_pairs_onsets,
                                             (cfg('preprocess', 'early_re_referencing', 'stim_excl_epoch')[0], cfg('preprocess', 'early_re_referencing', 'stim_excl_epoch')[1]),
                                             channel_key_seperator='-')
    if late_reref is not None:
        late_reref.set_exclude_reref_epochs(stim_pairs_onsets,
                                            (cfg('preprocess', 'late_re_referencing', 'stim_excl_epoch')[0], cfg('preprocess', 'late_re_referencing', 'stim_excl_epoch')[1]),
                                            channel_key_seperator='-')
    logging.info('')


    #
    # read and epoch the data
    #

    # determine the metrics that should be produced
    metric_callbacks = tuple()
    if cfg('metrics', 'cross_proj', 'enabled'):
        metric_callbacks += tuple([MetricCrossProj.process_callback])
    if cfg('metrics', 'waveform', 'enabled'):
        metric_callbacks += tuple([MetricWaveform.process_callback])

    # read, normalize, epoch and average the trials within the condition
    # Note: 'load_data_epochs_averages' is used instead of 'load_data_epochs' here because it is more memory
    #       efficient when only the averages are needed
    if len(metric_callbacks) == 0:
        logging.info('- Reading data...')
    else:
        logging.info('- Reading data and calculating metrics...')

    # TODO: normalize to raw or to Z-values (return both raw and z?)
    #       z-might be needed for detection
    try:
        sampling_rate, averages, metrics = load_data_epochs_averages(bids_subset_data_path, channels_measured_incl, stim_pairs_onsets,
                                                                     trial_epoch=cfg('trials', 'trial_epoch'),
                                                                     baseline_norm=cfg('trials', 'baseline_norm'),
                                                                     baseline_epoch=cfg('trials', 'baseline_epoch'),
                                                                     out_of_bound_handling=cfg('trials', 'out_of_bounds_handling'),
                                                                     metric_callbacks=metric_callbacks,
                                                                     high_pass=cfg('preprocess', 'high_pass'),
                                                                     early_reref=early_reref,
                                                                     line_noise_removal=line_noise_removal,
                                                                     late_reref=late_reref,
                                                                     preproc_priority=('speed' if preproc_prioritize_speed else 'mem'))
    except (ValueError, RuntimeError):
        logging.error('Could not load data (' + bids_subset_data_path + '), exiting...')
        raise RuntimeError('Could not load data')

    # split out the metric results
    cross_proj_metrics = None
    waveform_metrics = None
    metric_counter = 0
    if cfg('metrics', 'cross_proj', 'enabled'):
        cross_proj_metrics = np.array(metrics[:, :, metric_counter].tolist())
        metric_counter += 1
    if cfg('metrics', 'waveform', 'enabled'):
        waveform_metrics = np.array(metrics[:, :, metric_counter].tolist())
        metric_counter += 1

    # for each stimulation pair condition, NaN out the values of the measured electrodes that were stimulated
    for stim_pair_index, stim_pair in enumerate(stim_pairs_onsets):
        stim_pair_electrode_names = stim_pair.split('-')

        # find and clear the first electrode
        try:
            averages[channels_measured_incl.index(stim_pair_electrode_names[0]), stim_pair_index, :] = np.nan
            if cfg('metrics', 'cross_proj', 'enabled'):
                cross_proj_metrics[channels_measured_incl.index(stim_pair_electrode_names[0]), stim_pair_index, :] = np.nan
            if cfg('metrics', 'waveform', 'enabled'):
                waveform_metrics[channels_measured_incl.index(stim_pair_electrode_names[0]), stim_pair_index] = np.nan

        except ValueError:
            pass

        # find and clear the second electrode
        try:
            averages[channels_measured_incl.index(stim_pair_electrode_names[1]), stim_pair_index, :] = np.nan
            if cfg('metrics', 'cross_proj', 'enabled'):
                cross_proj_metrics[channels_measured_incl.index(stim_pair_electrode_names[1]), stim_pair_index, :] = np.nan
            if cfg('metrics', 'waveform', 'enabled'):
                waveform_metrics[channels_measured_incl.index(stim_pair_electrode_names[1]), stim_pair_index] = np.nan

        except ValueError:
            pass

    # determine the sample of stimulus onset (counting from the epoch start)
    onset_sample = int(round(abs(cfg('trials', 'trial_epoch')[0] * sampling_rate)))
    # todo: handle trial epochs which start after the trial onset, currently disallowed by config


    #
    # intermediate saving of the CCEP data as .mat
    #

    output_dict = dict()
    output_dict['sampling_rate'] = sampling_rate
    output_dict['onset_sample'] = onset_sample
    output_dict['ccep_average'] = averages
    output_dict['stimpair_labels'] = np.asarray(list(stim_pairs_onsets.keys()), dtype='object')
    output_dict['channel_labels'] = np.asarray(channels_measured_incl, dtype='object')
    output_dict['epoch_time_s'] = (np.arange(averages.shape[2]) - onset_sample) / sampling_rate
    output_dict['config'] = get_config_dict()
    if cfg('metrics', 'cross_proj', 'enabled'):
        MetricCrossProj.append_output_dict_callback(output_dict, cross_proj_metrics)
    if cfg('metrics', 'waveform', 'enabled'):
        MetricWaveform.append_output_dict_callback(output_dict, waveform_metrics)

    sio.savemat(os.path.join(output_root, 'erdetect_data.mat'), output_dict)

    # write the configuration
    write_config(os.path.join(output_root, 'erdetect_config.json'))


    #
    # perform the evoked response detection
    #

    # detect evoked responses
    logging.info('- Detecting evoked responses...')
    try:
        method = cfg('detection', 'method')
        evaluate_method = None
        if method == 'cross_proj':
            evaluate_method = lambda c_i, sp_i, m=cross_proj_metrics : MetricCrossProj.evaluate_callback(c_i, sp_i, metric_values=m)
        elif method == 'waveform':
            evaluate_method = lambda c_i, sp_i, m=waveform_metrics : MetricWaveform.evaluate_callback(c_i, sp_i, metric_values=m)

        if cfg('detection', 'negative'):
            neg_peak_latency, er_neg_peak_amplitudes = ieeg_detect_er(averages, onset_sample, int(sampling_rate),
                                                                      evaluation_callback=evaluate_method)
        if cfg('detection', 'positive'):
            pos_peak_latency, er_pos_peak_amplitudes = ieeg_detect_er(averages, onset_sample, int(sampling_rate),
                                                                      evaluation_callback=evaluate_method,
                                                                      detect_positive=True)
    except (ValueError, RuntimeError):
        logging.error('Evoked response detection failed, exiting...')
        raise RuntimeError('Evoked response detection failed')

    # intermediate saving of the data and evoked response detection results as .mat
    if cfg('detection', 'negative'):
        output_dict['neg_peak_latency_samples'] = neg_peak_latency
        output_dict['neg_peak_latency_ms'] = (neg_peak_latency - onset_sample) / sampling_rate * 1000
        output_dict['neg_peak_amplitudes'] = er_neg_peak_amplitudes
    if cfg('detection', 'positive'):
        output_dict['pos_peak_latency_samples'] = pos_peak_latency
        output_dict['pos_peak_latency_ms'] = (pos_peak_latency - onset_sample) / sampling_rate * 1000
        output_dict['pos_peak_amplitudes'] = er_pos_peak_amplitudes
    sio.savemat(os.path.join(output_root, 'erdetect_data.mat'), output_dict)


    #
    # generate images
    #

    if cfg('visualization', 'generate_electrode_images') or \
        cfg('visualization', 'generate_stimpair_images') or \
        cfg('visualization', 'generate_matrix_images'):

        #
        # prepare some settings for plotting
        #

        # generate the x-axis values
        # Note: TRIAL_EPOCH_START is not expected to start after the stimulus onset, currently disallowed by config
        x = np.arange(averages.shape[2])
        x = x / sampling_rate + cfg('trials', 'trial_epoch')[0]

        # determine the range on the x-axis where the stimulus was in samples
        # Note: TRIAL_EPOCH_START is not expected to start after the stimulus onset, currently disallowed by config
        stim_start_x = int(round(abs(cfg('trials', 'trial_epoch')[0] - cfg('visualization', 'blank_stim_epoch')[0]) * sampling_rate)) - 1
        stim_end_x = stim_start_x + int(ceil(abs(cfg('visualization', 'blank_stim_epoch')[1] - cfg('visualization', 'blank_stim_epoch')[0]) * sampling_rate)) - 1

        # calculate the legend x position
        legend_x = cfg('visualization', 'x_axis_epoch')[1] - .13

        # determine the drawing properties
        plot_props = calc_sizes_and_fonts(OUTPUT_IMAGE_SIZE,
                                          len(stim_pairs_onsets),
                                          len(channels_measured_incl))

        #
        # generate the electrodes plot
        #
        if cfg('visualization', 'generate_electrode_images'):

            # make sure an electrode output directory exists
            electrodes_output = os.path.join(output_root, 'electrodes')
            if not os.path.exists(electrodes_output):
                try:
                    os.makedirs(electrodes_output)
                except OSError as e:
                    logging.error("Could not create subset electrode image output directory (\'" + electrodes_output + "\'), exiting...")
                    raise RuntimeError('Could not create electrode image output directory')

            #
            logging.info('- Generating electrode plots...')

            # create progress bar
            print_progressbar(0, len(channels_measured_incl), prefix='Progress:', suffix='Complete', length=50)

            # loop through electrodes
            for iElec in range(len(channels_measured_incl)):

                # create a figure and retrieve the axis
                fig = create_figure(OUTPUT_IMAGE_SIZE, plot_props['stimpair_y_image_height'], False)
                ax = fig.gca()

                # set the title
                ax.set_title(channels_measured_incl[iElec] + '\n', fontsize=plot_props['title_font_size'], fontweight='bold')

                # loop through the stimulation-pairs
                for iPair in range(len(stim_pairs_onsets)):

                    # draw 0 line
                    y = np.empty((averages.shape[2], 1))
                    y.fill(len(stim_pairs_onsets) - iPair)
                    ax.plot(x, y, linewidth=plot_props['zero_line_thickness'], color=(0.8, 0.8, 0.8))

                    # retrieve the signal
                    y = averages[iElec, iPair, :] / 500
                    y += len(stim_pairs_onsets) - iPair

                    # nan out the stimulation
                    #TODO, only nan if within display range
                    y[stim_start_x:stim_end_x] = np.nan

                    # check if there is a signal to plot
                    if not np.isnan(y).all():

                        # plot the signal
                        ax.plot(x, y, linewidth=plot_props['signal_line_thickness'])

                        # if negative evoked potential is detected, plot it
                        if cfg('visualization', 'negative') and not isnan(neg_peak_latency[iElec, iPair]):
                            x_neg = neg_peak_latency[iElec, iPair] / sampling_rate + cfg('trials', 'trial_epoch')[0]
                            y_neg = er_neg_peak_amplitudes[iElec, iPair] / 500
                            y_neg += len(stim_pairs_onsets) - iPair
                            ax.plot(x_neg, y_neg, marker='o', markersize=6, color='blue')

                        # if positive evoked potential is detected, plot it
                        if cfg('visualization', 'positive') and not isnan(pos_peak_latency[iElec, iPair]):
                            x_pos = pos_peak_latency[iElec, iPair] / sampling_rate + cfg('trials', 'trial_epoch')[0]
                            y_pos = er_pos_peak_amplitudes[iElec, iPair] / 500
                            y_pos += len(stim_pairs_onsets) - iPair
                            ax.plot(x_pos, y_pos, marker='^', markersize=7, color=(0, 0, .6))

                # set the x-axis
                ax.set_xlabel('\nTime (s)', fontsize=plot_props['axis_label_font_size'])
                ax.set_xlim(cfg('visualization', 'x_axis_epoch'))
                for label in ax.get_xticklabels():
                    label.set_fontsize(plot_props['axis_ticks_font_size'])

                # set the y-axis
                ax.set_ylabel('Stimulated electrode-pair\n', fontsize=plot_props['axis_label_font_size'])
                ax.set_ylim((0, len(stim_pairs_onsets) + 1))
                ax.set_yticks(np.arange(1, len(stim_pairs_onsets) + 1, 1))
                ax.set_yticklabels(np.flip(list(stim_pairs_onsets.keys())), fontsize=plot_props['stimpair_axis_ticks_font_size'])
                ax.spines['bottom'].set_linewidth(1.5)
                ax.spines['left'].set_linewidth(1.5)

                # draw legend
                legend_y = 2 if len(stim_pairs_onsets) > 4 else (1 if len(stim_pairs_onsets) > 1 else 0)
                ax.plot([legend_x, legend_x], [legend_y + .05, legend_y + .95], linewidth=plot_props['legend_line_thickness'], color=(0, 0, 0))
                ax.text(legend_x + .01, legend_y + .3, '500 \u03bcV', fontsize=plot_props['legend_font_size'])

                # hide the right and top spines
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)

                # save figure
                fig.savefig(os.path.join(electrodes_output, 'electrode_' + str(channels_measured_incl[iElec]) + '.png'), bbox_inches='tight')

                # update progress bar
                print_progressbar(iElec + 1, len(channels_measured_incl), prefix='Progress:', suffix='Complete', length=50)

        #
        # generate the stimulation-pair plots
        #
        if cfg('visualization', 'generate_stimpair_images'):

            # make sure a stim-pair output directory exists
            stimpairs_output = os.path.join(output_root, 'stimpairs')
            if not os.path.exists(stimpairs_output):
                try:
                    os.makedirs(stimpairs_output)
                except OSError as e:
                    logging.error("Could not create subset stim-pair image output directory (\'" + stimpairs_output + "\'), exiting...")
                    raise RuntimeError('Could not create stim-pair image output directory')

            #
            logging.info('- Generating stimulation-pair plots...')

            # create progress bar
            print_progressbar(0, len(stim_pairs_onsets), prefix='Progress:', suffix='Complete', length=50)

            # loop through the stimulation-pairs
            # Note: the key order in stim_pairs_onsets and the first dimension of the CCEP averages matrix should match
            iPair = 0
            for stim_pair in stim_pairs_onsets.keys():

                # create a figure and retrieve the axis
                fig = create_figure(OUTPUT_IMAGE_SIZE, plot_props['electrode_y_image_height'], False)
                ax = fig.gca()

                # set the title
                ax.set_title(stim_pair + '\n', fontsize=plot_props['title_font_size'], fontweight='bold')

                # loop through the electrodes
                for iElec in range(len(channels_measured_incl)):

                    # draw 0 line
                    y = np.empty((averages.shape[2], 1))
                    y.fill(len(channels_measured_incl) - iElec)
                    ax.plot(x, y, linewidth=plot_props['zero_line_thickness'], color=(0.8, 0.8, 0.8))

                    # retrieve the signal
                    y = averages[iElec, iPair, :] / 500
                    y += len(channels_measured_incl) - iElec

                    # nan out the stimulation
                    #TODO, only nan if within display range
                    y[stim_start_x:stim_end_x] = np.nan

                    # plot the signal
                    ax.plot(x, y, linewidth=plot_props['signal_line_thickness'])

                    # if evoked potential is detected, plot it
                    if cfg('visualization', 'negative') and not isnan(neg_peak_latency[iElec, iPair]):
                        x_neg = neg_peak_latency[iElec, iPair] / sampling_rate + cfg('trials', 'trial_epoch')[0]
                        y_neg = er_neg_peak_amplitudes[iElec, iPair] / 500
                        y_neg += len(channels_measured_incl) - iElec
                        ax.plot(x_neg, y_neg, marker='o', markersize=6, color='blue')

                    if cfg('visualization', 'positive') and not isnan(pos_peak_latency[iElec, iPair]):
                        x_pos = pos_peak_latency[iElec, iPair] / sampling_rate + cfg('trials', 'trial_epoch')[0]
                        y_pos = er_pos_peak_amplitudes[iElec, iPair] / 500
                        y_pos += len(channels_measured_incl) - iElec
                        ax.plot(x_pos, y_pos, marker='^', markersize=7, color=(0, 0, .6))

                # set the x-axis
                ax.set_xlabel('\nTime (s)', fontsize=plot_props['axis_label_font_size'])
                ax.set_xlim(cfg('visualization', 'x_axis_epoch'))
                for label in ax.get_xticklabels():
                    label.set_fontsize(plot_props['axis_ticks_font_size'])

                # set the y-axis
                ax.set_ylabel('Measured electrodes\n', fontsize=plot_props['axis_label_font_size'])
                ax.set_ylim((0, len(channels_measured_incl) + 1))
                ax.set_yticks(np.arange(1, len(channels_measured_incl) + 1, 1))
                ax.set_yticklabels(np.flip(channels_measured_incl), fontsize=plot_props['electrode_axis_ticks_font_size'])
                ax.spines['bottom'].set_linewidth(1.5)
                ax.spines['left'].set_linewidth(1.5)

                # draw legend
                legend_y = 2 if len(stim_pairs_onsets) > 4 else (1 if len(stim_pairs_onsets) > 1 else 0)
                ax.plot([legend_x, legend_x], [legend_y + .05, legend_y + .95], linewidth=plot_props['legend_line_thickness'], color=(0, 0, 0))
                ax.text(legend_x + .01, legend_y + .3, '500 \u03bcV', fontsize=plot_props['legend_font_size'])

                # Hide the right and top spines
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)

                # save figure
                fig.savefig(os.path.join(stimpairs_output, 'stimpair_' + stim_pair + '.png'), bbox_inches='tight')

                # update progress bar
                print_progressbar(iPair + 1, len(stim_pairs_onsets), prefix='Progress:', suffix='Complete', length=50)

                #
                iPair += 1


        #
        # generate the matrices
        #
        if cfg('visualization', 'generate_matrix_images'):

            #
            logging.info('- Generating matrices...')

            image_width, image_height = calc_matrix_image_size(plot_props['stimpair_y_image_height'],
                                                               len(stim_pairs_onsets),
                                                               len(channels_measured_incl))

            # generate negative matrices and save
            if cfg('visualization', 'negative'):

                # amplitude
                fig = gen_amplitude_matrix(list(stim_pairs_onsets.keys()), channels_measured_incl,
                                           plot_props, image_width, image_height,
                                           er_neg_peak_amplitudes.copy() * -1, False)
                fig.savefig(os.path.join(output_root, 'matrix_amplitude_neg.png'), bbox_inches='tight')

                # latency
                fig = gen_latency_matrix(list(stim_pairs_onsets.keys()), channels_measured_incl,
                                         plot_props, image_width, image_height,
                                         (neg_peak_latency.copy() - onset_sample) / sampling_rate * 1000)     # convert the indices (in samples) to time units (ms)
                fig.savefig(os.path.join(output_root, 'matrix_latency_neg.png'), bbox_inches='tight')

            # generate positive matrices and save
            if cfg('visualization', 'positive'):

                # amplitude
                fig = gen_amplitude_matrix(list(stim_pairs_onsets.keys()), channels_measured_incl,
                                           plot_props, image_width, image_height,
                                           er_pos_peak_amplitudes.copy(), True)
                fig.savefig(os.path.join(output_root, 'matrix_amplitude_pos.png'), bbox_inches='tight')

                # latency
                fig = gen_latency_matrix(list(stim_pairs_onsets.keys()), channels_measured_incl,
                                         plot_props, image_width, image_height,
                                         (pos_peak_latency.copy() - onset_sample) / sampling_rate * 1000)     # convert the indices (in samples) to time units (ms)
                fig.savefig(os.path.join(output_root, 'matrix_latency_pos.png'), bbox_inches='tight')

    #
    logging.info('- Finished subset')

    # remove the subset log handler and close the log file
    root_logger.removeHandler(subset_logger_file)
    subset_logger_file.close()

    # on success, return output
    return output_dict


def log_single_line(header, text, output=None):
    """
    Log a single line with header, spacing and text

    Args:
        header (str):                         Line header
        text (str):                           Line text
        output (None or list):                Where to output the line to. None to write to Logger.
                                              Pass list object to append the line to that list
    """
    if output is None:
        logging.info(header.ljust(LOGGING_CAPTION_INDENT_LENGTH, ' ') + text)
    else:
        output.append(header.ljust(LOGGING_CAPTION_INDENT_LENGTH, ' ') + text)


def log_text(text, output=None):
    """
    Log a text

    Args:
        text (str):                           Text to print
        output (None or list):                Where to output the line to. None to write to Logger.
                                              Pass list object to append the line to that list
    """
    if output is None:
        logging.info(text)
    else:
        output.append(text)


def log_config(preproc_prioritize_speed, output=None):
    """
    Print configuration information
    """

    log_single_line('Preprocessing priority:', ('Speed' if preproc_prioritize_speed else 'Memory'), output)
    log_single_line('High-pass filtering:', ('Yes' if cfg('preprocess', 'high_pass') else 'No'), output)
    log_single_line('Early re-referencing:', ('Yes' if cfg('preprocess', 'early_re_referencing', 'enabled') else 'No'), output)
    if cfg('preprocess', 'early_re_referencing', 'enabled'):
        log_single_line('    Method:', str(cfg('preprocess', 'early_re_referencing', 'method')), output)
        log_single_line('    Stim exclude epoch:', str(cfg('preprocess', 'early_re_referencing', 'stim_excl_epoch')[0]) + 's : ' + str(cfg('preprocess', 'early_re_referencing', 'stim_excl_epoch')[1]) + 's', output)
        log_text(multi_line_list(cfg('preprocess', 'early_re_referencing', 'channel_types'), LOGGING_CAPTION_INDENT_LENGTH, '    Included channels types:', 14, ' '), output)
    log_single_line('Line-noise removal:', cfg('preprocess', 'line_noise_removal') + (' Hz' if is_number(cfg('preprocess', 'line_noise_removal')) else ''), output)
    log_single_line('Late re-referencing:', ('Yes' if cfg('preprocess', 'late_re_referencing', 'enabled') else 'No'), output)
    if cfg('preprocess', 'late_re_referencing', 'enabled'):
        log_single_line('    Method:', str(cfg('preprocess', 'late_re_referencing', 'method')), output)
        if cfg('preprocess', 'late_re_referencing', 'method') in ('CAR', 'CAR_headbox'):
            log_single_line('    CAR by variance:', ('Off' if cfg('preprocess', 'late_re_referencing', 'CAR_by_variance') == -1 else 'Channels with lowest (' + str(cfg('preprocess', 'late_re_referencing', 'CAR_by_variance')) + ' quantile) trial variance'), output)
        log_single_line('    Stim exclude epoch:', str(cfg('preprocess', 'late_re_referencing', 'stim_excl_epoch')[0]) + 's : ' + str(cfg('preprocess', 'late_re_referencing', 'stim_excl_epoch')[1]) + 's', output)
        log_text(multi_line_list(cfg('preprocess', 'late_re_referencing', 'channel_types'), LOGGING_CAPTION_INDENT_LENGTH, '    Included channels types:', 14, ' '), output)
    log_text('')
    
    log_single_line('Trial epoch window:', str(cfg('trials', 'trial_epoch')[0]) + 's < stim onset < ' + str(cfg('trials', 'trial_epoch')[1]) + 's  (window size ' + str(abs(cfg('trials', 'trial_epoch')[1] - cfg('trials', 'trial_epoch')[0])) + 's)', output)
    log_single_line('Trial out-of-bounds handling:', str(cfg('trials', 'out_of_bounds_handling')), output)
    log_single_line('Trial baseline window:', str(cfg('trials', 'baseline_epoch')[0]) + 's : ' + str(cfg('trials', 'baseline_epoch')[1]) + 's', output)
    log_single_line('Trial baseline normalization:', str(cfg('trials', 'baseline_norm')), output)
    log_single_line('Concatenate bidirectional stimulated pairs:', ('Yes' if cfg('trials', 'concat_bidirectional_pairs') else 'No'), output)
    log_single_line('Minimum # of required stimulus-pair trials:', str(cfg('trials', 'minimum_stimpair_trials')), output)
    log_text(multi_line_list(cfg('channels', 'measured_types'), LOGGING_CAPTION_INDENT_LENGTH, 'Include channel types as measured:', 14, ' '), output)
    log_text(multi_line_list(cfg('channels', 'stim_types'), LOGGING_CAPTION_INDENT_LENGTH, 'Include channel types for stimulation:', 14, ' '), output)
    log_text('', output)

    log_single_line('Cross-projection metric:', ('Enabled' if cfg('metrics', 'cross_proj', 'enabled') else 'Disabled'), output)
    if cfg('metrics', 'cross_proj', 'enabled'):
        log_single_line('    Cross-projection epoch:', str(cfg('metrics', 'cross_proj', 'epoch')[0]) + 's : ' + str(cfg('metrics', 'cross_proj', 'epoch')[1]) + 's', output)
    log_single_line('Waveform metric:', ('Enabled' if cfg('metrics', 'waveform', 'enabled') else 'Disabled'), output)
    if cfg('metrics', 'waveform', 'enabled'):
        log_single_line('    Waveform epoch:', str(cfg('metrics', 'waveform', 'epoch')[0]) + 's : ' + str(cfg('metrics', 'waveform', 'epoch')[1]) + 's', output)
        log_single_line('    Waveform bandpass:', str(cfg('metrics', 'waveform', 'bandpass')[0]) + 'Hz - ' + str(cfg('metrics', 'waveform', 'bandpass')[1]) + 'Hz', output)
    log_text('', output)

    log_text('Detection', output)
    log_single_line('    Negative responses:', ('Yes' if cfg('detection', 'negative') else 'No'), output)
    log_single_line('    Positive responses:', ('Yes' if cfg('detection', 'positive') else 'No'), output)
    log_single_line('    Peak search window:', str(cfg('detection', 'peak_search_epoch')[0]) + 's : ' + str(cfg('detection', 'peak_search_epoch')[1]) + 's', output)
    log_single_line('    Evoked response search window:', str(cfg('detection', 'response_search_epoch')[0]) + 's : ' + str(cfg('detection', 'response_search_epoch')[1]) + 's', output)
    log_single_line('    Evoked response detection method:', str(cfg('detection', 'method')), output)
    if cfg('detection', 'method') == 'std_base':
        log_single_line('        Std baseline window:', str(cfg('detection', 'std_base', 'baseline_epoch')[0]) + 's : ' + str(cfg('detection', 'std_base', 'baseline_epoch')[1]) + 's', output)
        log_single_line('        Std baseline threshold factor:', str(cfg('detection', 'std_base', 'baseline_threshold_factor')), output)
    elif cfg('detection', 'method') == 'cross_proj':
        log_single_line('        Cross-projection detection threshold:', str(cfg('detection', 'cross_proj', 'threshold')), output)
    elif cfg('detection', 'method') == 'waveform':
        log_single_line('        Waveform detection threshold:', str(cfg('detection', 'waveform', 'threshold')), output)
    log_text('', output)
    log_text('Visualization', output)
    log_single_line('    Negative responses:', ('Yes' if cfg('visualization', 'negative') else 'No'), output)
    log_single_line('    Positive responses:', ('Yes' if cfg('visualization', 'positive') else 'No'), output)
    log_single_line('    X-axis epoch:', str(cfg('visualization', 'x_axis_epoch')[0]) + 's : ' + str(cfg('visualization', 'x_axis_epoch')[1]) + 's', output)
    log_single_line('    Blank stimulation epoch:', str(cfg('visualization', 'blank_stim_epoch')[0]) + 's : ' + str(cfg('visualization', 'blank_stim_epoch')[1]) + 's', output)
    log_single_line('    Generate electrode images:', ('Yes' if cfg('visualization', 'generate_electrode_images') else 'No'), output)
    log_single_line('    Generate stimulation-pair images:', ('Yes' if cfg('visualization', 'generate_stimpair_images') else 'No'), output)
    log_single_line('    Generate matrix images:', ('Yes' if cfg('visualization', 'generate_matrix_images') else 'No'), output)
    log_text('', output)
    log_text('', output)
    log_text('', output)
