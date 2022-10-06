from pathlib import Path
import log_reader

if __name__ == '__main__':

    path = Path(r'C:\Users\Msmt\Documents\GitHub\backup-tool\test\prototyping\config_prototype.py')

    log_watcher = log_reader.LogWatcher(path, 0.03)
    log_watcher.run()
