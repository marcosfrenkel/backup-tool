import logging
import os.path

import log

from pathlib import Path

from log import setup_logging
import checker

setup_logging(True, os.path.abspath('testing_log.log'))

def create_basic_structure(path: Path) -> None:
    # Create the src dir first
    src_dir = path.joinpath('src')
    src_project1 = src_dir.joinpath('project1')
    src_measurement = src_project1.joinpath('measurement')
    src_project2 = src_dir.joinpath('project2')
    src_simulation = src_project2.joinpath('simulation')

    # Create the dest paths now
    dest_dir = path.joinpath('dest')
    dest_project1 = dest_dir.joinpath('project1')
    dest_measurement = dest_project1.joinpath('measurement')
    dest_project2 = dest_dir.joinpath('project2')
    dest_simulation = dest_project2.joinpath('simulation')

    src_dir.mkdir()
    src_project1.mkdir()
    src_measurement.mkdir()
    src_project2.mkdir()
    src_simulation.mkdir()

    # Create the dest paths now
    dest_dir.mkdir()
    dest_project1.mkdir()
    dest_measurement.mkdir()
    dest_project2.mkdir()
    dest_simulation.mkdir()

def test_log_file_location(tmp_path):
    logger_location = tmp_path.joinpath('structure.log')
    logger = setup_logging(True, log_file=str(logger_location))

    logger.debug('HELLLO')
    logger.warning('warning')
    logger.error('ERROR ERROR ERROR')
    assert logger_location.is_file()


def test_basic_use(tmp_path):

    src_dir = tmp_path.joinpath('src')
    dest_dir = tmp_path.joinpath('dest')
    create_basic_structure(tmp_path)

    file_checker = checker.StructureChecker(src_dir, dest_dir)
    assert file_checker.problematic_folders == []



