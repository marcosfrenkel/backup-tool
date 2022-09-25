
import logging

from pathlib import Path
from log import *

# src_path = Path(r'C:\Users\Msmt\Documents\Python Scripts\back_playground\src')
# dest_path = Path(r'C:\Users\Msmt\Documents\Python Scripts\back_playground\dest')

logger = log_logger(__name__)


class StructureChecker:

    # TODO: Add checks to validate the passed paths
    def __init__(self, src: Path, dest: Path):
        print(f'what are you logger: {logger}')
        logger.info(f'creating structure checker')

        self.src = src
        self.src_len = len(src.parts)
        self.dest = dest
        self.dest_len = len(dest.parts)

        self.valid_names = ['measurement', 'simulation']

        self.problematic_folders = []
        logger.debug(f'starting folder check')
        self.check_folders()
        logger.debug(f'folder check complete')

    def check_folders(self):
        skip_folders = []

        for item in self.src.glob('**/*'):
            if item.is_dir():
                for skip in skip_folders:
                    if item.is_relative_to(skip):
                        logger.debug(f'{item} has been skipped since its related to: {skip}')
                        continue
                if item not in skip_folders:
                    if item.name in self.valid_names:
                        if item not in skip_folders:
                            skip_folders.append(item)
                            logger.debug(f'{item} added to skip_folders')
                    else:
                        path_parts = item.parts[self.src_len:]
                        target_path = self.dest
                        for part in path_parts:
                            target_path = target_path.joinpath(part)
                        if target_path.is_dir():
                            logger.debug(f'for item:{item} the target: {target_path} has been found :)')
                        else:
                            self.problematic_folders.append(target_path)
                            logger.debug(f'{target_path} NOT FOUND NOT FOUND')

