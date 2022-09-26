
from pathlib import Path

import checker
import log


if __name__ == '__main__':

    log.setup_logging(True, 'logging.log')

    src_path = Path(r'C:\Users\Msmt\Documents\Python Scripts\back_playground\src')
    dest_path = Path(r'C:\Users\Msmt\Documents\Python Scripts\back_playground\dest')

    file_checker = checker.StructureChecker(src_path, dest_path)



