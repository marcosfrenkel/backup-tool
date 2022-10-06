"""
First prototype of the file structure checker for the backup tool. For now the structure checker does not do anything
other than logging everything it finds into a logging file and variables.

The rules are the following:

    * All folders inside the source directory (with the allowed folders' exception) must exist in the dest source.
    * The only folders that are allowed to not exist in the dest source are folders named: "measurement" and "simulation".
        These folder should be created automatically in the dest equivalent spot.
        Anything inside the allowed folders is not checked and is going to be copied directly.
    * Before creating the StructureCheker object the user should call the log.setup_logging function to specify the
      location of the logging file.

"""

from typing import List, Tuple
from pathlib import Path
from log import *

logger = log_logger('filechecker')


class StructureChecker:
    """
    First prototype of the structure checker. Rules are in the docstring of the module.

    :param src: The path of the source directory.
    :param dest: The path of the destination directory.
    """
    def __init__(self, src: Path, dest: Path):
        self.src = src
        self.src_len = len(src.parts)
        self.dest = dest
        self.dest_len = len(dest.parts)

        self.valid_names = ['measurement', 'simulation']

        self.problematic_folders: List[Tuple[Path, Path]] = []
        self.data_folders: List[Path] = []
        self.create_data_folders: List[Tuple[Path, Path]] = []
        self.target_founds: List[Tuple[Path, Path]] = []
        self.skipped_folders: List[Path] = []
        logger.info(f'starting folder check')
        self.check_folders()
        logger.info(f'folder check complete')

    def reset_internal_variables(self) -> None:
        """
        Resets the variables used to keep track of the findings.
        """
        self.problematic_folders = []
        self.data_folders = []
        self.target_founds = []
        self.create_data_folders = []
        self.skipped_folders = []

    def convert_src_to_dest(self, path: Path) -> Path:
        """
        Converts the src into the dest path equivalent.

        :param path: The src you want to convert to dest path.
        :return: The converted dest path.
        """
        path_parts = path.parts[self.src_len:]
        target_path = self.dest
        for part in path_parts:
            target_path = target_path.joinpath(part)
        return target_path

    def check_folders(self) -> None:
        """
        Runs the folder check.
        """
        self.reset_internal_variables()

        for item in self.src.glob('**/*'):
            if item.is_dir():
                skip = False
                for data_folder in self.data_folders:
                    if item.is_relative_to(data_folder):
                        logger.debug(f'{item} has been skipped since its related to: {data_folder}.')
                        skip = True
                        self.skipped_folders.append(item)
                        break
                if not skip:
                    if item not in self.data_folders:
                        if item.name in self.valid_names:
                            self.data_folders.append(item)
                            logger.debug(f'{item} added to data_folders.')

                            target_path = self.convert_src_to_dest(item)
                            if not target_path.is_dir():
                                self.create_data_folders.append((item, target_path))
                                logger.debug(f'{item} is being created in dest.')

                        else:
                            target_path = self.convert_src_to_dest(item)
                            if target_path.is_dir():
                                self.target_founds.append((item, target_path))
                                logger.debug(f'for item:{item} the target: {target_path} has been found :)')
                            else:
                                self.problematic_folders.append((item, target_path))
                                logger.error(f'{item} has not been found in {target_path}')

