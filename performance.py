#!/usr/bin/env python

###@@@ pylint does not work from command-line and also not in editor

import argparse
import logging
import os
import time

def main():
    args = parse_command_line_arguments()
    report_args(args)
    performance_measurement(args)

def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description='Python Logging Performance Analysis')
    parser.add_argument(
        '--iterations',
        type=int,
        default=1000,
        help='Number of iterations; default 1000')
    parser.add_argument(
        '--message-level',
        type=level,
        default='error', 
        help='Message level (critical, error, warning, info, debug); default error')
    parser.add_argument(
        '--logger-level', 
        type=level, 
        default='error', 
        help='Logger level (critical, error, warning, info, debug); default error')
    args = parser.parse_args()
    return args

def level(string):
    string = string.lower()
    if string == 'critical':
        return logging.CRITICAL
    elif string == 'error':
        return logging.ERROR
    elif string == 'warning':
        return logging.WARNING
    elif string == 'info':
        return logging.INFO
    elif string == 'debug':
        return logging.DEBUG
    else:
        msg = "{} is not a valid level".format(string)
        raise argparse.ArgumentTypeError(msg)

def report_args(args):
    print("Number of iterations : {} secs".format(args.iterations))
    print("Message level        : {}".format(level_to_str(args.message_level)))
    print("Logger level         : {}".format(level_to_str(args.logger_level)))
    print()

def level_to_str(level):
    if level == logging.CRITICAL:
        return "CRITICAL"
    elif level == logging.ERROR:
        return "ERROR"
    elif level == logging.WARNING:
        return "WARNING"
    elif level == logging.INFO:
        return "INFO"
    elif level == logging.DEBUG:
        return "DEBUG"
    else:
        assert False

def performance_measurement(args):
    logger = create_logger(args)
    start_time = time.perf_counter()
    iteration = 1
    while iteration <= args.iterations:
        log_no_filter_no_args(logger)
        iteration += 1
    time.sleep(2.1)
    end_time = time.perf_counter()
    total_elapsed_secs = end_time - start_time
    usecs_per_iteration = 1000000.0 * total_elapsed_secs / args.iterations
    print("Total elapsed time   : {:.3f} secs".format(total_elapsed_secs))
    print("Time per iteration   : {:.3f} usecs".format(usecs_per_iteration))

def select_log_function(args):
    log_functions = [
        (logging.CRITICAL, log_critical),
        (logging.ERROR,    message_error),
        (logging.WARNING,  message_warning),
        (logging.INFO,     message_info),
        (logging.DEBUG,    message_debug),
    ]
    for (message_level, log_function) in log_functions:
        if message_level == args.message_level:
            return log_function
    assert False, "Could not find log function that matches command line arguments"

def log_critical(logger):
    logger.critical("This is a critical message")

def message_error(logger):
    logger.critical("This is an error message")

def message_error(logger):
    logger.critical("This is an error message")

def create_logger(args):
    log_file_name = "performance.log"
    if os.path.exists(log_file_name):
        os.remove(log_file_name)
    logging.basicConfig(
        filename=log_file_name,
        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
        level=args.logger_level)
    logger = logging.getLogger('performance')
    return logger

if __name__ == "__main__":
    main()
