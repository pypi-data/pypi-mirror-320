# MIT License
#
# Copyright (C) 2019 The Little Hackers.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import annotations

import logging
import sys

from thelittlehackers.constant.logging import LOGGING_LEVELS
from thelittlehackers.constant.logging import LoggingLevelLiteral


DEFAULT_LOGGING_FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
DEFAULT_LOGGING_LEVEL = LoggingLevelLiteral.INFO


def get_console_handler(
        logging_formatter: logging.Formatter | None = DEFAULT_LOGGING_FORMATTER
) -> logging.StreamHandler:
    """
    Create and return a console logging handler that outputs to the
    system's standard output.

    This handler formats log messages using the provided ``Formatter``
    instance or the default formatter if none is specified.


    :param logging_formatter: The ``Formatter`` instance to use for
        formatting log records.  Defaults to ``DEFAULT_LOGGING_FORMATTER``.


    :return: A configured ``StreamHandler`` that writes formatted log
        records to the standard output.
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging_formatter)
    return console_handler


def set_up_logger(
        logging_formatter: logging.Formatter | None = DEFAULT_LOGGING_FORMATTER,
        logging_level: LoggingLevelLiteral | None = DEFAULT_LOGGING_LEVEL,
        logger_name: str = None
) -> logging.Logger:
    """
    Configure a logger to output log messages to the system's standard
    output.

    This function sets up a logging handler with a specified formatter and
    logging level.  If no logger name is provided, the handler is attached
    to the root logger.


    :param logging_formatter: An instance of ``Formatter`` used to format
        log records.  Defaults to ``DEFAULT_LOGGING_FORMATTER``.

    :param logging_level: The logging threshold for the logger.  Log
        messages with a severity lower than this level will be ignored.
        Messages at this level or higher will be emitted by the configured
        handler(s), unless a handler's level is set to a higher severity
        than the specified ``logging_level``.  Defaults to `
        `DEFAULT_LOGGING_LEVEL``.

    :param logger_name: The name of the logger to configure.  If ``None``,
        the handler will be attached to the root logger.


    :return: A configured ``Logger`` instance.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOGGING_LEVELS[logging_level or DEFAULT_LOGGING_LEVEL])
    logger.addHandler(get_console_handler(logging_formatter=logging_formatter))
    logger.propagate = False
    return logger
