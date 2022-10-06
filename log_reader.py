"""
Have the permissions the slack app needs to have so that this works.
"""

import os
import re
import time
import importlib.util
from importlib.machinery import ModuleSpec
from pathlib import Path
from typing import Optional, Dict, Generator, Union, List

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.client import SlackResponse

# TODO: Test what happens when different fields in the config file are not present.


def reverse_readline(filename, buf_size=8192) -> Generator:
    """A generator that returns the lines of a file in reverse order

    taken from: https://stackoverflow.com/questions/2301789/how-to-read-a-file-in-reverse-order
    """
    with open(filename) as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split('\n')
            # The first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # If the previous chunk starts right from the beginning of line
                # do not concat the segment to the last line of new chunk.
                # Instead, yield the segment first
                if buffer[-1] != '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index]
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment


class SlackCommunicator:
    """
    Object in charge of sending messages to slack. Used to send messages from other objects.
    """

    def __init__(self, config: dict):
        """
        Constructor for SlackCommunicator.

        :param config: The complete configuration dictionary taken from the configuration file.
        """
        self.config = config
        self.client = WebClient(token=config['token'])

        self.users: Dict[str, str] = {}
        self.channels: Dict[str, str] = {}

        self.load_users()
        self.load_channels()

        self.send_message(":robot_face: _beep boop_ :robot_face: ENGAGED :robot_face: _beep boop_ :robot_face:")

    def __del__(self) -> None:
        """
        Sends closing message to slack.
        """
        self.send_message(':skull: _boop beep_ :skull: DISENGAGED :skull: _boop beep_ :skull:')

    def load_users(self) -> None:
        """
        Goes through all the users in the Slack workplace and creates a dictionary mapping the users name to their ids.
        Raises a SlackApiError if there is an error trying to get the users.
        """
        try:
            for result in self.client.users_list():
                for user in result['members']:
                    self.users[user['name']] = user['id']
        except SlackApiError as e:
            raise e

    def load_channels(self) -> None:
        """
        Goes through all the channels in the Slack workplace and creates a dictionary mapping the users name to their ids.
        Raises a SlackApiError if there is an error trying to get the channels.
        """
        try:
            for result in self.client.conversations_list():
                for channel in result["channels"]:
                    self.channels[channel["name"]] = channel['id']
        except SlackApiError as e:
            raise e

    def send_message(self, message: str, message_config: Optional[dict] = None) -> \
            Optional[SlackResponse]:
        """
        Sends message to the Slack workplace.

        :param message: The string to send
        :param message_config: Optional config dictionary. This dictionary should have the field 'channel' with the
            channel name to which to send the message. It can also have the field 'tag' with a list of users names that
            should be tagged in the message. If 'all' is in the tag list, the channel itself will be tagged.
        :return: The response from Slack after sending the message.
        """
        if message_config is None:
            message_config = self.config['status']

        channel_id = self.channels[message_config['channel']]
        if 'tag' in message_config:
            tags_str = ''
            for user in message_config['tag']:
                if user == 'all':
                    tags_str = tags_str + '<!channel>, '
                else:
                    tags_str = tags_str + f'<@{self.users[user]}>, '
            message = tags_str + message
        try:
            return self.client.chat_postMessage(channel=channel_id, text=message, )
        except SlackApiError as e:
            print(f'Error: {e}')
            return None


class LogReaderEventHandler(FileSystemEventHandler):
    """
    Custom event handler for watchdog. When a modified file gets triggered, checks that the modified file is in the
    config dictionary and reports updates of new lines in slack depending on the configuration.
    Any lines that have been written before initializing this object will not be reported.
    """

    def __init__(self, config: dict, communicator: SlackCommunicator, date_fmt: str = '%Y-%m-%d %H:%M:%S'):
        """
        Constructor for LogReaderEventHandler.

        :param config: The complete configuration dictionary taken from the configuration file.
        :param communicator: An instance of SlackCommunicator.
        :param date_fmt: The string format of the date format. Default, '%Y-%m-%d %H:%M:%S'.
        """
        super().__init__()
        self.config = config
        self.communicator = communicator

        self.date_fmt = date_fmt

        # Dictionary with the tracked files as keys, and their last reported lines time as values.
        # Used to know when to stop reading the file. Gets created with current time.
        self.files = {x: time.time() for x in config['files'].keys()}

    # TODO: add some kind of check that the log file has the correct structure, what happens if sections have other
    #  sections that I am not expecting.
    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Gets called when a file in a monitoring directory gets modified. Checks if that file is a log file that it's
        keeping track and sends the new log lines into the specified Slack channels. The log messages should be
        separated by the character '|', the first section should be time following the format of the parameter
        data_fmt, the second the name of the module writing the line, the third the level of the log message and
        lastly the fourth the message itself .

        :param event: The on_modified event.
        """
        src_path = str(event.src_path)

        # A file that's not the log file in the same directory might trigger on_modified.
        if src_path in self.files:
            reverse_line_generator = reverse_readline(src_path)
            new_time = time.time()
            for line in reverse_line_generator:
                sections = line.split("|")
                line_time = time.mktime(time.strptime(re.sub(r'\t+', '', sections[0]), self.date_fmt))

                # Stop iterating when we get to a message older than the last time we checked
                if line_time <= self.files[src_path]:
                    break

                category = re.sub(r'\t+| +', '', sections[2])
                if category in self.config:
                    self.communicator.send_message(sections[0] + ':' + sections[2] + ':' + sections[3],
                                                   self.config[category])
            self.files[src_path] = new_time


class LogWatcher:
    """
    Keeps track of whatever log files are in the files key of the config dictionary and post any updates in a slack
    channel in real time. See config file documentation on how to write it. To use just create an instance of this
    object in a script, pass it the path of the config file and call the run function. The LogWatcher will run
    indefinitely.
    """
    def __init__(self, conf_path: Path, resend_period: Union[int, float] = 1):
        """
        Constructor of LogWatcher

        :param conf_path: The path of the config file.
        :param resend_period: The time period, in hours, which the watcher
            will send a message if there hasn't been any updates for the specified period of a specific log file.
        """

        spec = importlib.util.spec_from_file_location(conf_path.name, conf_path)
        assert isinstance(spec, ModuleSpec)
        assert spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        assert mod is not None
        spec.loader.exec_module(mod)

        self.config = mod.config

        self.communicator = SlackCommunicator(self.config)

        self.event_handler = LogReaderEventHandler(self.config, self.communicator)
        self.observer = Observer()
        self.last_message_sent = {}
        for file in self.config['files'].keys():
            self.observer.schedule(self.event_handler, str(Path(file).parent), recursive=False)
            self.last_message_sent[file] = time.time()

        self.resend_period = resend_period * 3600

    def run(self) -> None:
        """
        Starts the watchdog observer
        """
        self.observer.start()
        try:
            while True:
                current_t = time.time()
                for file, file_conf in self.config['files'].items():
                    if 'period' in file_conf:
                        last_update = self.event_handler.files[file]

                        if current_t - last_update > file_conf['period'] * 3600 \
                                and current_t - self.last_message_sent[file] > self.resend_period:
                            message_conf = file_conf.copy()
                            del message_conf['period']
                            self.communicator.send_message(
                                f'{file} has not received an update after {file_conf["period"]} hrs', message_conf)
                            self.last_message_sent[file] = current_t
                time.sleep(1)
        finally:
            self.observer.stop()
            self.observer.join()
