"""
Sample of config dictionary for the LogReader. To specify how the LogReader is going to behave, it needs to find a
python file with a dictionary called config.

The dictionary must have at most 8 different keys, 2 of which are special keys:

    * 'files': The files key indicate what logging files the LogReader should monitor. It must be a dictionary whose keys
        are the file paths to monitor. The values are again another nested dictionary with the following keys:
            * 'period': The period, in hours, key indicates how often this file should receive updates.
                E.g: If a backup should happen every 24 hours, this period should be 24, so that the LogReader knows
                that the backup did not happen at the right time.
            * 'channel': The channel where alarms respecting the periodicity of the updates should go.
                E.g: What channel does the LogReader sends a warning if the log did not receive the appropriate updates.
            * 'tag': Optional, A list containing what users should be tagged.
                If 'all' is in the list, the channel will be tagged. If 'tag' is not present, no users will be tagged
                in the message.

    * 'token': The Slack app authentication token.

The other 6 are optional and all have the same structure. They are keys that specify where the different levels of
 logging levels should go. All of them have dictionary as values that look have the same structure,
 they hold 2 different keys:

    * 'channel': The channel on which to send the messages regarding that level of message.
    * 'tag': Optional. List of usernames to tag for updates of that level.

The 6 levels are:
    * 'status': sending messages for general updates about the LogReader itself.
    * 'DEBUG': sending messages for DEBUG level logs.
    * 'INFO': sending messages for INFO level logs.
    * 'WARNING': sending messages for WARNING level logs.
    * 'ERROR': sending messages for ERROR level logs.
    * 'CRITICAL': sending messages for ERROR level logs.
"""

config = {
    'files': {r"path.log": {'period': 0.03,
                            'channel': 'general',
                            'tag': ['all']}},
    'token': "xoxb-",
    'status': {'channel': 'extra-channel'},
    'DEBUG': {'channel': 'random'},
    'INFO': {'channel': 'general',
             'tag': ['all']},
    'WARNING': {'channel': 'general',
                'tag': ['user1']},
    'ERROR': {'channel': 'extra-channel',
              'tag': ['user1', 'user2']},
}
