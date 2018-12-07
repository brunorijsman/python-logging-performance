#!/usr/bin/env python

import logging
import os
import sys
import time

import table

LOG_FILE_NAME = "performance.log"
ITERATIONS = 10000

LOG_METHOD_ARGS = 0
LOG_METHOD_PERCENT = 1
LOG_METHOD_FORMAT = 2

global_parameter_expense = None

def main():
    global global_parameter_expense
    scenarios = [
    #    Message level     Logger level      Nr par  Par expense  Log method
        (logging.CRITICAL, logging.CRITICAL, 0,      None,        LOG_METHOD_ARGS),
        (logging.CRITICAL, logging.CRITICAL, 0,      500,         LOG_METHOD_ARGS),
        (logging.ERROR,    logging.CRITICAL, 0,      None,        LOG_METHOD_ARGS),
        (logging.CRITICAL, logging.CRITICAL, 2,      None,        LOG_METHOD_ARGS),
        (logging.CRITICAL, logging.CRITICAL, 2,      None,        LOG_METHOD_PERCENT),
        (logging.CRITICAL, logging.CRITICAL, 2,      None,        LOG_METHOD_FORMAT),
        (logging.ERROR,    logging.CRITICAL, 2,      None,        LOG_METHOD_ARGS),
        (logging.ERROR,    logging.CRITICAL, 2,      None,        LOG_METHOD_PERCENT),
        (logging.ERROR,    logging.CRITICAL, 2,      None,        LOG_METHOD_FORMAT),
        (logging.CRITICAL, logging.CRITICAL, 2,      500,         LOG_METHOD_ARGS),
        (logging.CRITICAL, logging.CRITICAL, 2,      500,         LOG_METHOD_PERCENT),
        (logging.CRITICAL, logging.CRITICAL, 2,      500,         LOG_METHOD_FORMAT),
        (logging.ERROR,    logging.CRITICAL, 2,      500,         LOG_METHOD_ARGS),
        (logging.ERROR,    logging.CRITICAL, 2,      500,         LOG_METHOD_PERCENT),
        (logging.ERROR,    logging.CRITICAL, 2,      500,         LOG_METHOD_FORMAT),
    ]
    if os.path.exists(LOG_FILE_NAME):
        os.remove(LOG_FILE_NAME)
    logging.basicConfig(filename=LOG_FILE_NAME, 
                        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    logger = logging.getLogger('performance')
    tab = table.Table()
    tab.add_row([["Message", "Level"],
                 ["Logger", "Level"],
                 ["Parameter", "Count"],
                 ["Parameter", "Expense"],
                 ["Log", "Method"],
                 ["Lines", "Logged"],
                 ["Iteration", "usecs"]])
    for scenario in scenarios:
        (message_level, logger_level, nr_parameters, parameter_expense, log_method) = scenario
        run_scenario(tab, logger, message_level, logger_level, nr_parameters, parameter_expense,
                     log_method)
    print(tab.to_string())

def run_scenario(tab, logger, message_level, logger_level, nr_parameters, parameter_expense,
                 log_method):
    global global_parameter_expense
    lines_before = lines_in_log_file()
    logger.setLevel(logger_level)
    baseline_elapsed_secs = measure_loop(logger, no_op)
    log_function = select_log_function(message_level, nr_parameters, log_method)
    global_parameter_expense = parameter_expense
    total_elapsed_secs = measure_loop(logger, log_function)
    adjusted_elapsed_secs = total_elapsed_secs - baseline_elapsed_secs
    usecs_per_iteration = 1000000.0 * adjusted_elapsed_secs / ITERATIONS
    lines_after = lines_in_log_file()
    added_lines = lines_after - lines_before
    tab.add_row([level_str(message_level),
                 level_str(logger_level),
                 nr_parameters,
                 parameter_expense,
                 log_method_str(log_method),
                 added_lines,
                 "{:.3f}".format(usecs_per_iteration)])

def level_str(level):
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

def log_method_str(method):
    if method == LOG_METHOD_ARGS:
        return "args"
    elif method == LOG_METHOD_PERCENT:
        return "percent"
    elif method == LOG_METHOD_FORMAT:
        return "format"
    else:
        assert False

def select_log_function(message_level, nr_parameters, log_method):
    if message_level == logging.CRITICAL:
        if nr_parameters == 0:
            return log_critical_0_par
        elif nr_parameters == 2:
            if log_method == LOG_METHOD_ARGS:
                return log_critical_2_par_args
            elif log_method == LOG_METHOD_PERCENT:
                return log_critical_2_par_percent
            elif log_method == LOG_METHOD_FORMAT:
                return log_critical_2_par_format
            else:
                sys.exit("No log function for log method")
        else:
            sys.exit("No log function for number of parameters")
    elif message_level == logging.ERROR:
        if nr_parameters == 0:
            return log_error_0_par
        elif nr_parameters == 2:
            if log_method == LOG_METHOD_ARGS:
                return log_error_2_par_args
            elif log_method == LOG_METHOD_PERCENT:
                return log_error_2_par_percent
            elif log_method == LOG_METHOD_FORMAT:
                return log_error_2_par_format
            else:
                sys.exit("No log function for log method")
        else:
            sys.exit("No log function for number of parameters")
    else:
        sys.exit("No log function for message severity")

def measure_loop(logger, log_function):
    start_time = time.perf_counter()
    iteration = 1
    while iteration <= ITERATIONS:
        log_function(logger)
        iteration += 1
    end_time = time.perf_counter()
    elapsed_secs = end_time - start_time
    return elapsed_secs

def no_op(_logger):
    pass

def log_error_0_par(logger):
    logger.error("This is an error message")

def log_critical_0_par(logger):
    logger.critical("This is a critical message")

def log_error_2_par_args(logger):
    logger.error("This is an error message: x=%s y=%s", x_par(), y_par())

def log_critical_2_par_args(logger):
    logger.critical("This is a critical message: x=%s y=%s", x_par(), y_par())

def log_error_2_par_percent(logger):
    logger.error("This is an error message: x=%s y=%s" % (x_par(), y_par()))

def log_critical_2_par_percent(logger):
    logger.critical("This is a critical message: x=%s y=%s" % (x_par(), y_par()))

def log_error_2_par_format(logger):
    logger.error("This is an error message: x={} y={}".format(x_par(), y_par()))

def log_critical_2_par_format(logger):
    logger.critical("This is a critical message: x={} y={}".format(x_par(), y_par()))

def x_par():
    global global_parameter_expense
    if global_parameter_expense is not None:
        incur_expense(global_parameter_expense)
    return "this-is-the-value-for-x"

def y_par():
    global global_parameter_expense
    if global_parameter_expense is not None:
        incur_expense(global_parameter_expense)
    return "this-is-the-value-for-y"

def incur_expense(expense):
    dummy = 1
    i = 0
    while i < expense:
        dummy = 2 * dummy - 1
        i += 1

def lines_in_log_file():
    if not os.path.exists(LOG_FILE_NAME):
        return 0
    count = 0
    return sum(1 for line in open(LOG_FILE_NAME))

if __name__ == "__main__":
    main()
