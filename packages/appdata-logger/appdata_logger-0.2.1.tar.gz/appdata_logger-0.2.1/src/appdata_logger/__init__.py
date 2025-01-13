# -*- coding: utf-8 -*-
import datetime
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List

# noinspection SpellCheckingInspection
TIME_AND_LEVEL_WITHOUT_NAME_FORMAT = '%(asctime)s %(levelname)8s: %(message)s'
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def create_separate_log_path(
        log_folder: Path, make_dirs: bool = True, caller_file_path: str = None) -> Path:
    if caller_file_path is None:
        caller_file_path = sys.argv[0]
    executable_name, _extension = os.path.splitext(os.path.basename(caller_file_path))
    # noinspection PyUnresolvedReferences,PyProtectedMember
    start_time = datetime.datetime.fromtimestamp(logging._startTime)
    start_time_string = start_time.isoformat('-').replace(':', '-')
    if make_dirs:
        os.makedirs(log_folder, exist_ok=True)
    pid = os.getpid()
    return log_folder / f'{executable_name}-{start_time_string}-{pid}.txt'


def create_separate_file_handler(
        log_folder: Path, make_dirs: bool = True, caller_file_path: str = None) -> logging.Handler:
    return logging.FileHandler(
        create_separate_log_path(log_folder=log_folder, make_dirs=make_dirs, caller_file_path=caller_file_path),
        mode='w',
        encoding='utf-8'
    )


class StdOutFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno < logging.WARNING


def create_stdout_and_stderr_handlers() -> List[logging.Handler]:
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.addFilter(StdOutFilter())
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    return [stdout_handler, stderr_handler]


def create_console_and_file_handlers(
        log_folder: Path,
        make_dirs: bool = True,
        caller_file_path: str = None,
        separate_stdout_and_stderr: bool = False,
) -> List[logging.Handler]:
    if separate_stdout_and_stderr:
        result = create_stdout_and_stderr_handlers()
    else:
        result = [logging.StreamHandler(sys.stdout)]
    return result + [
        create_separate_file_handler(log_folder=log_folder, make_dirs=make_dirs, caller_file_path=caller_file_path),
    ]


def get_appdata_log_folder(application: str) -> Path:
    return Path(os.getenv('APPDATA')) / application


# noinspection PyShadowingBuiltins,SpellCheckingInspection
def config_with_console_and_file_handlers(
        application: str,
        make_dirs: bool = True,
        caller_file_path: str = None,
        level: int = logging.INFO,
        format: str = TIME_AND_LEVEL_WITHOUT_NAME_FORMAT,
        datefmt: str = DATE_TIME_FORMAT,
        separate_stdout_and_stderr: bool = False,
) -> None:
    log_folder = get_appdata_log_folder(application)
    logging.basicConfig(
        level=level,
        format=format,
        datefmt=datefmt,
        handlers=create_console_and_file_handlers(
            log_folder=log_folder,
            make_dirs=make_dirs,
            caller_file_path=caller_file_path,
            separate_stdout_and_stderr=separate_stdout_and_stderr,
        ),
    )


def log_command_line() -> None:
    command_line = subprocess.list2cmdline(sys.argv)
    logger = logging.getLogger()
    logger.info(command_line)
