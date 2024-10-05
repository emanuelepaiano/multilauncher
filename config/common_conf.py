import os 

# launch folder
LAUNCHER_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/../launchers"

# message secret key (message prefix for unique message)
MESSAGE_PREFIX_KEY = ''

# logging functions
LOG_ON_FILE=False
LOGFILE = 'multi-launcher.log'
LOGGING_FORMATTER = "%(asctime)s; %(name)s; %(levelname)s; %(message)s"
LOG_LEVEL = 'INFO'

# run stop commands for each stoppable on exit
ON_EXIT_STOP_ALL=False

# enable listeners
listener_enabled_flags = {
    'mqtt': True,
    'tcp': False,
    'udp': False,
    'rabbitmq': False
}

# it can be 'quit' or 'reconnect' if error happens
ON_ERROR='reconnect'



MULTILAUNCHER_SCRIPT_PLACEHOLDER='{MULTILAUNCHER_SCRIPTS_DIR}'
MULTILAUNCHER_SCRIPTS_FOLDER=os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")) + "/tools/scripts"