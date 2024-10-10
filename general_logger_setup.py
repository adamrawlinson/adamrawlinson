"""A module to house the setup of a fully formatted multi-handler logger."""


import datetime
import json
import logging
import logging.handlers
import os
from typing import Literal


# Shamelessly stolen from Bogdan Mircea: 
# https://stackoverflow.com/questions/50144628/python-logging-into-file-as-a-dictionary-or-json
# TODO: when appending to a file, multiple log entries result in improperly formed
#       json file. Requires further dev to ensure all entries form into singular object.
class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.

    @param dict fmt_dict: Key: logging format attribute pairs. Defaults to {"message": "message"}.
    @param str time_format: time.strftime() format string. Default: "%Y-%m-%dT%H:%M:%S"
    @param str msec_format: Microsecond formatting. Appended at the end. Default: "%s.%03dZ"
    """
    def __init__(self, fmt_dict: dict = None, time_format: str = "%Y-%m-%dT%H:%M:%S", msec_format: str = "%s.%03dZ"):
        self.fmt_dict = fmt_dict if fmt_dict is not None else {"message": "message"}
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    def usesTime(self) -> bool:
        """
        Overwritten to look for the attribute in the format dict values instead of the fmt string.
        """
        return "asctime" in self.fmt_dict.values()

    def formatMessage(self, record) -> dict:
        """
        Overwritten to return a dictionary of the relevant LogRecord attributes instead of a string. 
        KeyError is raised if an unknown attribute is provided in the fmt_dict. 
        """
        return {fmt_key: record.__dict__[fmt_val] for fmt_key, fmt_val in self.fmt_dict.items()}

    def format(self, record) -> str:
        """
        Mostly the same as the parent's class method, the difference being that a dict is manipulated and dumped as JSON
        instead of a string.
        """
        record.message = record.getMessage()
        
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str, indent=4, sort_keys=True)


class CustomTerminalFormat(logging.Formatter):
    """Custom terminal formatting including colour and bolding"""

    FORMATS = {
        logging.DEBUG: '\x1b[1;37m%(levelname)s\x1b[0m|%(asctime)s|\x1b[32;1m%(names)s\x1b[0m| %(message)s',
        logging.INFO: '\x1b[34;1m%(levelname)s\x1b[0m|%(asctime)s|\x1b[32;1m%(names)s\x1b[0m| %(message)s',
        logging.WARNING: '\x1b[33;1m%(levelname)s\x1b[0m|%(asctime)s|\x1b[32;1m%(names)s\x1b[0m|\x1b[33;21m %(message)s\x1b[0m',
        logging.ERROR: '\x1b[31;1m%(levelname)s\x1b[0m|%(asctime)s|\x1b[32;1m%(names)s\x1b[0m|\x1b[31;21m %(message)s\x1b[0m',
        logging.CRITICAL: '\x1b[37;1;41m%(levelname)s\x1b[0m|\x1b[37;1;41m%(asctime)s\x1b[0m|\x1b[37;1;41m%(names)s\x1b[0m|\x1b[37;1;41m %(message)s\x1b[0m',
    }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')

        return formatter.format(record)
    

def general_logger(
    logger_name: str = 'general_log',
    critical_email_host_address: list[str] = [],
    critical_email_address_list: list[str] = [],
    critical_email_subject: str = 'CRITICAL level triggered',
    email_credentials: tuple[str, str] = None,
    mail_host_detail: str = 'localhost',
    log_file_type: Literal['log', 'json'] = 'log',
    log_file_path: str = (
        f'{os.path.dirname(os.path.realpath(__file__))}'
        f"\\{datetime.datetime.now().strftime('%Y_%m_%d')}_general_log"
    )
) -> logging.Logger:
    """A general use logger that provides colour coded terminal logging,
    a .log or .json file and email for critical events.

    ARGS
        logger_name: str
            A str name to be used as the name arg for the getLogger
            function. If a child logger is to be used in other modules,
            it will require this name with a full stop + additional name
            e.g. 'main_logger' (parent) / 'main_logger.child_module.py'
            (child).

        critical_email_host_address: list[str]
            A str list of email address(es) to be passed through the
            fromaddr arg in the SMTPHandler function.
        
        critical_email_address_list: list[str]
            A str list of email addresses to be passed through the
            toaddrs arg in the SMTPHandler function.

        critical_email_subject: str
            A str for the subject field for the critical event email.
            default set as 'CRITICAL level triggered'.

        email_credentials: tuple[str, str]
            A username, password str tuple to be passed through the 
            credentials arg for the SMTPHandler function. Default set
            as None if no credentials required.

        mail_host_detail: str
            A str to be passed through the mailhost arg in the SMTPHandler
            function.
    
        log_file_type: Literal['log', 'json']
            A choice between a .log file or .json file as an output,
            if neither of these options are chosen no file will be
            produced. Default is set to 'log' to produce a .log file.

        log_file_path: str
            A str path (including name but excluding file extension) for
            the log file. The file extension will be determined via the 
            log_file_type arg. Default is to create a file wherever the
            script generating the logger is contained, with an ISO 8601
            dated file name: YYYY_MM_DD_general_log.

    RETURNS
        Returns a logging.Logger set up with multiple custom formatted
        handlers.
    """
    
    general_use_log = logging.getLogger(logger_name)
    general_use_log.setLevel('DEBUG')
    general_use_log.propagate = True

    if log_file_type == 'log':
        log_file_handler = logging.FileHandler(f'{log_file_path}.{log_file_type}', mode='a')
        log_file_handler.setLevel('INFO')
        logfile_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        log_file_handler.setFormatter(logfile_format)
    
    elif log_file_type == 'json':
        log_file_handler = logging.FileHandler(f'{log_file_path}.{log_file_type}', mode='a')
        log_file_handler.setLevel('INFO')
        json_formatter = JsonFormatter(
            {
                "level": "levelname", 
                "message": "message", 
                "loggerName": "name", 
                "processName": "processName",
                "processID": "process", 
                "threadName": "threadName", 
                "threadID": "thread",
                "timestamp": "asctime"
            }
        )
        log_file_handler.setFormatter(json_formatter)

    terminal_handler = logging.StreamHandler()
    terminal_handler.setLevel('DEBUG')
    terminal_format = CustomTerminalFormat()
    terminal_handler.setFormatter(terminal_format)

    critical_email_handler = logging.handlers.SMTPHandler(
        mailhost=mail_host_detail,
        fromaddr=critical_email_host_address,
        toaddrs=critical_email_address_list,
        subject=critical_email_subject,
        credentials=email_credentials
    )
    critical_email_handler.setLevel('CRITICAL')
    
    general_use_log.addHandler(log_file_handler)
    general_use_log.addHandler(terminal_handler)
    general_use_log.addHandler(critical_email_handler)

    return general_use_log