#!/usr/bin/env python3
"""
Evoked response detection - command-line entry-point
=====================================================
Command-line entry-point script for the automatic detection of evoked responses in CCEP data.


Copyright 2023, Max van den Boom (Multimodal Neuroimaging Lab, Mayo Clinic, Rochester MN)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import argparse
import logging
import os
import sys
import datetime
from bids_validator import BIDSValidator

# add a system path to ensure the absolute imports can be used
if not __package__:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PACKAGE_DIR = os.path.dirname(SCRIPT_DIR)
    if PACKAGE_DIR not in sys.path:
        sys.path.insert(0, PACKAGE_DIR)

# package imports
from erdetect.version import __version__
from erdetect.core.config import (
    load_config, get as cfg, set as cfg_set, rem as cfg_rem,\
    LOGGING_CAPTION_INDENT_LENGTH, CONFIG_DETECTION_STD_BASE_BASELINE_EPOCH_DEFAULT, \
    CONFIG_DETECTION_STD_BASE_BASELINE_THRESHOLD_FACTOR, CONFIG_DETECTION_STD_BASE_BASELINE_MIN_STD,
    CONFIG_DETECTION_CROSS_PROJ_THRESHOLD, CONFIG_DETECTION_WAVEFORM_PROJ_THRESHOLD
)
from erdetect._erdetect import process_subset
from ieegprep import VALID_FORMAT_EXTENSIONS
from ieegprep.bids.data_structure import list_bids_datasets
from ieegprep.utils.console import multi_line_list
from ieegprep.utils.misc import is_number
from erdetect._erdetect import log_single_line, log_config
from erdetect.views.gui import open_gui


def execute():

    #
    # define and parse the input arguments
    #
    parser = argparse.ArgumentParser(description='Automatically detect evoked responses in CCEP data.',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     add_help=False)
    parser._positionals.title = 'Required (positional) arguments'
    parser._optionals.title = 'Optional arguments'
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help='Show this help message and exit\n\n')
    parser.add_argument('bids_dir',
                        help='The directory with the input dataset formatted according to the BIDS standard.\n\n')
    parser.add_argument('output_dir',
                        help='The directory where the output files should be stored. If you are running group\n'
                             'level analysis this folder should be prepopulated with the results of the\n'
                             'participant level analysis.\n\n')
    parser.add_argument('--gui',
                        help='Run with the graphical user interface\n\n',
                        action='store_true')
    parser.add_argument('--participant_label',
                        help='This argument can be used to indicate which specific participant(s) in the BIDS\n'
                             'directory should be analyzed. The given label(s) should correspond to the\n'
                             'sub-<participant_label> as described in the BIDS specification. Label matching is\n'
                             'case-insensitive and \'sub-\' prefixes in any of the labels will be ignored.\n'
                             'If this parameter is not provided then all subjects will be analyzed. Multiple\n'
                             'participants can be specified with a space separated list.\n\n',
                        nargs="+")
    parser.add_argument('--subset_search_pattern',
                        help='This argument can be used to ensure that a specific text has to occur in the\n'
                             '(data) subset name for it to be analyzed. The pattern could be part of a BIDS\n'
                             'compliant folder name (e.g. \'task-ccep_run-01\'). The search is case-insensitive.\n'
                             'If this parameter is not provided then all the data subset(s) that are found will be\n'
                             'analyzed. Multiple search patterns can be specified with a space separated list.\n\n',
                        nargs="+")
    parser.add_argument('--format_extension',
                        help='Can be used to limit the data format(s) to include. The format(s) should be specified\n'
                             'by their extension (e.g. \'.edf\'). If this parameter is not provided, then by default\n'
                             'the European Data Format (\'.edf\'), BrainVision (\'.vhdr\', \'.vmrk\', \'.eeg\')\n'
                             'and MEF3 (\'.mefd\') formats will be included. Multiple formats can be specified\n'
                             'with a space separated list.\n\n',
                        nargs="+")
    parser.add_argument('--config_filepath',
                        help='Configures the app according to the settings in the JSON configuration file\n\n')
    parser.add_argument('--apply_bids_validator',
                        help='Apply the BIDS data-set validation\n\n',
                        action='store_true')
    parser.add_argument('--preproc_prioritize_speed',
                        help='Prioritize preprocessing for speed rather than for memory. By default, while preprocessing,\n'
                             'priority is given to use as little memory as possible, which can require channel-data to be\n'
                             'retrieved twice, taking longer. This flag allows the preprocessing to keep channel-data\n'
                             'in memory, requiring much more memory at it''s peak, but speeding up the process.\n\n',
                        action='store_true')
    parser.add_argument('--high_pass',
                        help='Perform high-pass filtering (with a cut-off at 0.50Hz) before detection and visualization.\n'
                             'Note: If a configuration file is provided, then this command-line argument will overrule the\n'
                             '      high-pass setting in the configuration file\n\n',
                        action='store_true')
    parser.add_argument('--early_reref',
                        help='Perform early re-referencing (before line-noise removal) as part of the processing\n'
                             'preceding detection and visualization. The options are:\n'
                             '      - CAR          = Common Average Re-referencing (e.g. \'--early_reref CAR\')\n'
                             '      - CAR_headbox  = Common Average Re-referencing per headbox (e.g. \'--early_reref CAR_headbox\').'
                             '                       The headbox number should be indicated for each channel in '
                             '                       the _channels.tsv file in a column with the heading \'headbox\'.\n'
                             'Note: If a configuration file is provided, then this command-line argument will overrule the\n'
                             '      early re-referencing setting in the configuration file\n\n',
                        nargs=1)
    parser.add_argument('--line_noise_removal',
                        help='Perform line-noise removal before detection and visualization. Can be either:\n'
                             '      - \'json\' or \'sidecar\' to lookup the line-noise frequency in the BIDS *_ieeg.json file\n'
                             '        (e.g. \'--line_noise_removal json\')\n'
                             '      - set to a specific line-noise frequency (e.g. \'--line_noise_removal 60\')\n'
                             'Note: If a configuration file is provided, then this command-line argument will overrule the\n'
                             '      line-noise removal setting in the configuration file\n\n',
                        nargs="?", const='json')
    parser.add_argument('--late_reref',
                        help='Perform late re-referencing (after line-noise removal) as part of the processing\n'
                             'preceding detection and visualization. The options are:\n'
                             '      - CAR          = Common Average Re-referencing (e.g. \'--late_reref CAR\')\n'
                             '      - CAR_headbox  = Common Average Re-referencing per headbox (e.g. \'--late_reref CAR_headbox\').'
                             '                       The headbox number should be indicated for each channel in '
                             '                       the _channels.tsv file in a column with the heading \'headbox\'.\n'
                             'Note: If a configuration file is provided, then this command-line argument will overrule the\n'
                             '      late re-referencing setting in the configuration file\n\n',
                        nargs=1)
    parser.add_argument('--late_reref_CAR_by_variance',
                        help='Perform late re-referencing by applying a common average for each stim-pair condition\n'
                             '(per group) where it''s average is based on only the channels with the lowest trial signal variance.\n'
                             'Note: If a configuration file is provided, then this command-line argument will overrule the\n'
                             '      late re-referencing by variance setting in the configuration file\n\n',
                        nargs='?', const='0.2')
    parser.add_argument('--include_positive_responses',
                        help='Detect and visualize positive evoked responses in addition to the negative responses\n\n',
                        action='store_true')
    parser.add_argument('--method',
                        help='The method that should be used to detect evoked responses. the options are:\n'
                             '      - std_base   = The standard deviation of a baseline-epoch is used as a threshold\n'
                             '                     (multiplied by a factor) to determine whether the average evoked deflection\n'
                             '                     is strong enough. (e.g. \'--method std_base\')\n'
                             '      - cross-proj = Cross-projection of the trials is used to determine the inter-trial\n'
                             '                     similarity. A peak with a strong inter-trial similarity is\n'
                             '                     considered an evoked response. (e.g. \'--method cross-proj\')\n'
                             '      - waveform   = Searches for the typical (20Hz oscillation) shape of the average response\n'
                             '                     to determine whether the peak that was found can be considered an evoked.\n'
                             '                     response (e.g. \'--method waveform\')\n'
                             'Note: If a configuration file is provided, then this command-line argument will overrule the\n'
                             '      method setting in the configuration file\n\n',
                        nargs="?")
    parser.add_argument('-v', '--version',
                        action='version',
                        version='ER-Detect version {}'.format(__version__))
    args = parser.parse_args()


    #
    # make sure the output directory exists
    #

    # TODO: potentially the logging output can be written here from now on as well
    if not os.path.exists(args.output_dir):
        try:
            os.makedirs(args.output_dir)
        except OSError as e:
            logging.error('Could not create output directory (\'' + args.output_dir + '\'), exiting...')
            return 1

    # start general log in output directory
    logger = logging.getLogger()
    logger_file = logging.FileHandler(os.path.join(args.output_dir, 'erdetect__' + datetime.datetime.now().strftime("%Y%m%d__%H%M%S") + '.log'))
    logger_file.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(logger_file)


    #
    # display application information
    #
    logging.info('------------------------ Evoked Response Detection - v' + __version__ + ' ------------------------')
    logging.info('')


    #
    # configure
    #
    if args.config_filepath:
        log_single_line('Input configuration file:', args.config_filepath)
        logging.info('')

    #  read the configuration file (if passed)
    if args.config_filepath:
        if not load_config(args.config_filepath):
            logging.error('Could not load the configuration file, exiting...')
            return 1

    # check preprocessing arguments
    preproc_prioritize_speed = False
    if args.preproc_prioritize_speed:
        preproc_prioritize_speed = True

    if args.high_pass:
        cfg_set(True, 'preprocess', 'high_pass')

    if args.line_noise_removal:
        if str(args.line_noise_removal).lower() == 'json' or str(args.line_noise_removal).lower() == 'sidecar':
            cfg_set('JSON', 'preprocess', 'line_noise_removal')
        elif is_number(args.line_noise_removal):
            # TODO: valid number
            cfg_set(str(args.line_noise_removal), 'preprocess', 'line_noise_removal')
        else:
            logging.error('Invalid \'line_noise_removal\' argument \'' + args.line_noise_removal + '\', either set to \'json\' or \'sidecar\' to retrieve the line-noise frequency from the *_ieeg.json file, or provide the line-noise frequency as a number.')
            return 1

    if args.early_reref:
        if str(args.early_reref[0]).lower() == 'car':
            cfg_set(True, 'preprocess', 'early_re_referencing', 'enabled')
            cfg_set('CAR', 'preprocess', 'early_re_referencing', 'method')
        elif str(args.early_reref[0]).lower() == 'car_headbox':
            cfg_set(True, 'preprocess', 'early_re_referencing', 'enabled')
            cfg_set('CAR_headbox', 'preprocess', 'early_re_referencing', 'method')
        else:
            logging.error('Invalid \'early_reref\' argument \'' + args.early_reref[0] + '\'')
            return 1

    if args.late_reref:
        if str(args.late_reref[0]).lower() == 'car':
            cfg_set(True, 'preprocess', 'late_re_referencing', 'enabled')
            cfg_set('CAR', 'preprocess', 'late_re_referencing', 'method')
        elif str(args.late_reref[0]).lower() == 'car_headbox':
            cfg_set(True, 'preprocess', 'late_re_referencing', 'enabled')
            cfg_set('CAR_headbox', 'preprocess', 'late_re_referencing', 'method')
        else:
            logging.error('Invalid \'late_reref\' argument \'' + args.late_reref[0] + '\'')
            return 1

    if args.late_reref_CAR_by_variance:
        if not cfg('preprocess', 'late_re_referencing', 'enabled') or not cfg('preprocess', 'late_re_referencing', 'method') in ('CAR', 'CAR_headbox'):
            logging.error('The \'late_reref_CAR_by_variance\' argument is set, but can only be used while using a late CAR re-referencing method.\n'
                          'Make sure the \'late_reref\' argument is set to either CAR or CAR_headbox')
            return 1
        if is_number(args.late_reref_CAR_by_variance):
            late_reref_CAR_by_variance = float(args.late_reref_CAR_by_variance)
            if late_reref_CAR_by_variance < 0 or late_reref_CAR_by_variance > 1:
                logging.error('Invalid \'late_reref_CAR_by_variance\' argument \'' + str(late_reref_CAR_by_variance) + '\', should be a value between 0 and 1 (default is 0.2).')
                return 1
            cfg_set(late_reref_CAR_by_variance, 'preprocess', 'late_re_referencing', 'CAR_by_variance')
        else:
            logging.error('Invalid \'late_reref_CAR_by_variance\' argument \'' + args.late_reref_CAR_by_variance + '\', provide a quantile as a value between 0 and 1 (default is 0.2).')
            return 1

    # check for methodological arguments
    if args.include_positive_responses:
        cfg_set(True, 'detection', 'positive')
        cfg_set(True, 'visualization', 'positive')

    # if negative or positive response visualization is enabled, make sure detection is as well
    if cfg('visualization', 'negative') and not cfg('detection', 'negative'):
        logging.warning('Visualization of negative evoked responses is enabled, but the detection is set to disabled, detection of negative responses will be enabled')
        cfg_set(True, 'detection', 'negative')
    if cfg('visualization', 'positive') and not cfg('detection', 'positive'):
        logging.warning('Visualization of positive evoked responses is enabled, but the detection is set to disabled, detection of positive responses will be enabled')
        cfg_set(True, 'detection', 'positive')

    if args.method:
        cfg_rem('detection', 'std_base')
        cfg_rem('detection', 'cross_proj')
        cfg_rem('detection', 'waveform')
        if args.method == "std_base":
            cfg_set('std_base', 'detection', 'method')
            cfg_set(CONFIG_DETECTION_STD_BASE_BASELINE_EPOCH_DEFAULT, 'detection', 'std_base', 'baseline_epoch')
            cfg_set(CONFIG_DETECTION_STD_BASE_BASELINE_THRESHOLD_FACTOR, 'detection', 'std_base', 'baseline_threshold_factor')
            cfg_set(CONFIG_DETECTION_STD_BASE_BASELINE_MIN_STD, 'detection', 'std_base', 'baseline_minimum_std')
        elif args.method == "cross_proj":
            cfg_set('cross_proj', 'detection', 'method')
            cfg_set(CONFIG_DETECTION_CROSS_PROJ_THRESHOLD, 'detection', 'cross_proj', 'threshold')
        elif args.method == "waveform":
            cfg_set('waveform', 'detection', 'method')
            cfg_set(CONFIG_DETECTION_WAVEFORM_PROJ_THRESHOLD, 'detection', 'waveform', 'threshold')
        else:
            logging.error('Invalid method argument \'' + args.method + '\', pick one of the following: \'std_base\', \'cross_proj\' or \'waveform\'')
            return 1

    # if a metric is used for detection, enable them
    if cfg('detection', 'method') == 'cross_proj' and not cfg('metrics', 'cross_proj', 'enabled'):
        logging.warning('Evoked response detection is set to use cross-projections but the cross-projection metric is disabled, the cross-projection metric will be enabled')
        cfg_set(True, 'metrics', 'cross_proj', 'enabled')
    if cfg('detection', 'method') == 'waveform' and not cfg('metrics', 'waveform', 'enabled'):
        logging.warning('Evoked response detection is set to use waveforms but the waveform metric is disabled, the waveform metric will be enabled')
        cfg_set(True, 'metrics', 'waveform', 'enabled')


    #
    # open GUI or CLI processing
    #

    if args.gui:

        # open and run on theGUI
        open_gui(init_input_directory=args.bids_dir, init_output_directory=args.output_dir)

    else:

        # print configuration
        log_config(preproc_prioritize_speed)


        #
        # Find and process participants and their datasets
        #

        args.bids_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(args.bids_dir)))
        args.output_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(args.output_dir)))

        logging.info('--------------------------------- Participants and data subsets ----------------------------------')
        log_single_line('BIDS input path:', args.bids_dir)
        log_single_line('Output path:', args.output_dir)
        logging.info('')

        # print optional search arguments
        optional_search_argument = False
        if args.participant_label:
            log_single_line('Participant(s) to include:', ", ".join(args.participant_label))
            optional_search_argument = True
        if args.subset_search_pattern:
            log_single_line('Subset search pattern(s):', ", ".join(args.subset_search_pattern))
            optional_search_argument = True
        if args.format_extension:
            log_single_line('Only include subsets with data extension(s):', ", ".join(args.format_extension))
            optional_search_argument = True
        if optional_search_argument:
            logging.info('')

        # check if the input is a valid BIDS dataset
        if args.apply_bids_validator:
            #process = run_cmd('bids-validator %s' % args.bids_dir)
            #logging.info(process.stdout)
            #if process.returncode != 0:
            #    logging.error('BIDS input dataset did not pass BIDS validator. Datasets can be validated online '
            #                    'using the BIDS Validator (http://incf.github.io/bids-validator/).\nRun the detection '
            #                    'without the --apply_bids_validator argument to skip prior BIDS validation.')
            #    return 1
            bids_error = False
            for dir_, d, files in os.walk(args.bids_dir):
                for file in files:
                    rel_file = os.path.relpath(dir_, args.bids_dir)
                    if rel_file[0] == '.':
                        rel_file = rel_file[1:]
                    rel_file = os.path.join(rel_file, file)
                    if not BIDSValidator().is_bids('/' + rel_file):
                        logging.error('Invalid BIDS-file: ' + rel_file)
                        bids_error = True
            if bids_error:
                logging.error('BIDS input dataset did not pass the BIDS validator. Datasets can be validated online '
                              'using the BIDS Validator (http://incf.github.io/bids-validator/).\nRun the detection '
                              'without the --apply_bids_validator argument to skip prior BIDS validation.')
                return 1

        # list the datasets
        strict_search = True if args.apply_bids_validator else False
        datasets = list_bids_datasets(args.bids_dir,
                                      dataset_extensions=VALID_FORMAT_EXTENSIONS,
                                      subjects_filter=args.participant_label,
                                      subset_search_pattern=args.subset_search_pattern, strict_search=strict_search,
                                      only_subjects_with_subsets=True)

        #
        if len(datasets) == 0:

            logging.info('')
            if optional_search_argument:
                logging.warning('No datasets were found...\n'
                                'Input arguments might have limited the search, make sure to check your CLI arguments')
            else:
                logging.warning('No datasets were found...')

        else:

            # display subject/subset information
            logging.info('Participant(s) and subset(s) found:')
            for (subject, subsets) in datasets.items():
                short_subsets = [os.path.splitext(os.path.basename(os.path.normpath(x)))[0] for x in subsets]
                short_subsets = [x[0:-5] if x.endswith('_ieeg') else x for x in short_subsets]
                short_subsets = [x[0:-4] if x.endswith('_eeg') else x for x in short_subsets]
                logging.info(multi_line_list(list(short_subsets), LOGGING_CAPTION_INDENT_LENGTH, '    ' + subject + ':', 1, ' '))
            logging.info('')

            # process
            for (subject, subsets) in datasets.items():
                for subset in subsets:

                    # empty space
                    logging.info('')
                    logging.info('')
                    logging.info('')

                    # process
                    try:
                        process_subset(subset, args.output_dir, preproc_prioritize_speed)
                    except RuntimeError:
                        logging.error('Error while processing dataset, exiting...')
                        return 1

        # empty space and end message
        logging.info('')
        logging.info('')
        logging.info('')
        logging.info('--------------------------------------   Finished running   --------------------------------------')

    # return success exit code
    return 0


if __name__ == "__main__":
    sys.exit(execute())
