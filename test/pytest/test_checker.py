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


def test_file_creation(tmp_path):
    create_basic_structure(tmp_path)

    src_path = tmp_path.joinpath('src')
    dest_path = tmp_path.joinpath('dest')

    assert src_path.is_dir()
    assert dest_path.is_dir()


def test_basic_example(tmp_path):
    src_path = tmp_path.joinpath('src')
    dest_path = tmp_path.joinpath('dest')

    create_basic_structure(tmp_path)
    file_checker = checker.StructureChecker(src_path, dest_path)
    assert len(file_checker.problematic_folders) == 0
    assert len(file_checker.target_founds) == 2
    assert len(file_checker.data_folders) == 2
    assert len(file_checker.create_data_folders) == 0


def test_having_extra_folder_in_dest(tmp_path):
    create_basic_structure(tmp_path)

    src_path = tmp_path.joinpath('src')
    dest_path = tmp_path.joinpath('dest')

    dest_project1 = dest_path.joinpath('project1')
    extra_folder = dest_project1.joinpath('extra_folder')
    extra_file = extra_folder.joinpath('file.txt')
    extra_folder.mkdir()

    with open(str(extra_file), 'w') as f:
        f.write('text_file')

    file_checker = checker.StructureChecker(src_path, dest_path)
    assert len(file_checker.problematic_folders) == 0
    assert len(file_checker.target_founds) == 2
    assert len(file_checker.data_folders) == 2
    assert len(file_checker.create_data_folders) == 0


def test_having_extra_folder_in_src(tmp_path):
    create_basic_structure(tmp_path)

    src_path = tmp_path.joinpath('src')
    dest_path = tmp_path.joinpath('dest')

    src_project1 = src_path.joinpath('project1')
    extra_folder = src_project1.joinpath('extra_folder')
    extra_folder.mkdir()

    file_checker = checker.StructureChecker(src_path, dest_path)
    assert len(file_checker.problematic_folders) == 1
    assert file_checker.problematic_folders[0][0] == extra_folder
    assert len(file_checker.target_founds) == 2
    assert len(file_checker.data_folders) == 2
    assert len(file_checker.create_data_folders) == 0


def test_copying_new_allowed_folder(tmp_path):
    create_basic_structure(tmp_path)

    src_path = tmp_path.joinpath('src')
    dest_path = tmp_path.joinpath('dest')

    src_project3 = src_path.joinpath('project3')
    dest_project3 = dest_path.joinpath('project3')

    src_simulation = src_project3.joinpath('simulation')
    src_measurement = src_project3.joinpath('measurement')
    dest_simulation = dest_project3.joinpath('simulation')
    dest_measurement = dest_project3.joinpath('measurement')

    src_project3.mkdir()
    dest_project3.mkdir()
    src_simulation.mkdir()
    src_measurement.mkdir()

    file_checker = checker.StructureChecker(src_path, dest_path)
    assert len(file_checker.problematic_folders) == 0
    assert len(file_checker.target_founds) == 3
    assert len(file_checker.data_folders) == 4
    assert len(file_checker.create_data_folders) == 2

    src_data_folders = [item[0] for item in file_checker.create_data_folders]
    dest_data_folders = [item[1] for item in file_checker.create_data_folders]
    assert src_simulation in src_data_folders
    assert src_measurement in src_data_folders
    assert dest_simulation in dest_data_folders
    assert dest_measurement in dest_data_folders





