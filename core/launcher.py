from types import SimpleNamespace
from typing import Dict, List
import json
import config.common_conf as common_conf
from os import listdir, system
from os.path import isfile, join
import logging as logger
import subprocess
import os

log = logger.getLogger(__name__)

# Singleton define for classes above
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# ManLoaderager class is a singleton used to parse launcher from config files into dictionaries 
class Loader(metaclass=Singleton):
    """Runner class is a singleton used to parse launcher from config files into dictionaries 
    """
    __extension = '.json'

    def __parse_json(self, json_input) -> Dict:
        """Parse Json string to dictionary.

        ``json_input``: json string to be parsed
        """
        return json.loads(json_input, object_hook=lambda d: SimpleNamespace(**d))

    def __get_launcher_files(self, folder='') -> List:
        """return launcher file list.

        ``folder``: folder where .json launcher file are located
        """
        try: 
            return [f for f in listdir(folder) if isfile(join(folder, f)) and f.endswith(self.__extension)]
        except Exception as e:
            log.error("Error while opening directory " + folder + ": " + str(e))
            raise e

    def __get_file_content(self, filename):
        """map file content into a string.

        ``filename``: target file
        """
        try:
            file = open(filename, 'r')
            content = file.read()
            file.close()
            return content
        except Exception as e:
            log.error("Error while reading " + filename +": " + str(e))
            raise e


    def get_launchers(self, launcher_folder=common_conf.LAUNCHER_FOLDER) -> List:
        """return all launcher objects

        ``launcher_folder``: folder where .json launcher file are located. If not specified, will be used value common.LAUNCHER_FOLDER
        """
        launchers = []
        fileList = self.__get_launcher_files(launcher_folder)
        for file in fileList:
            try:
                content = self.__get_file_content(launcher_folder + "/" + file)
                launcher = self.__parse_json(content)
                log.debug("loaded config for " + str(launcher.name))
                launchers.append(launcher)
            except Exception as e:
                log.warning("[-] Ignoring file " + file +": " + str(e))
                pass
        return launchers

# Manager is a singleton used to dispatch message and start/stop launchers command. 
# It will passed to a Listener and run execute() method as handler
class Manager(metaclass=Singleton):
    """ LaunchManager is a singleton used to dispatch message and start/stop launchers command. 
    """
    __launcher_loader = None
    __launchers = []

    @property
    def launchers(self) -> List:
        return self.__launchers

    def __init__(self, launcher_loader = Loader()) -> None:
        """create a (single) instance of manager, you need to pass a custom LaunchLoader object

        ``launcher_loader``: launcher loader used to load launchers configuration
        """
        self.__launcher_loader = launcher_loader
        self.__launchers = self.__launcher_loader.get_launchers()
        for launcher in self.__launchers:
            launcher.is_running = False


    def __can_stop(self, launcher):
        """check if a launcher can be stopped. It return true or false

        ``launcher``: current launcher
        """
        return launcher.can_be_stopped

    def __can_start(self, launcher):
        """check if a launcher can be started

        ``launcher``: current launcher
        """
        if not launcher.multiple_instances:
            return not launcher.is_running and launcher.enabled
        else:
            return launcher.enabled

    def __start_launcher(self, launcher) -> None:
        """check condition with __can_start() and start a launcher

        ``launcher``: current launcher
        """
        if self.__can_start(launcher):
            log.info("starting " + launcher.name + " using command '" + launcher.start_command + "'")
            result = self.__run_shell(launcher.start_command)
            if result==0:
                launcher.is_running = True
        
    def __stop_launcher(self, launcher) -> None:
        """check condition with __can_stop() and stop a launcher

        ``launcher``: current launcher
        """
        if self.__can_stop(launcher) and launcher.is_running:
            log.info("stopping " + launcher.name + " using command '" + launcher.stop_command + "'")
            result = self.__run_shell(launcher.stop_command)
            if result==0:
                launcher.is_running = False

    def __run_shell(self, cmd):
        try:
            if cmd is not None:
                cmd = cmd.replace(common_conf.MULTILAUNCHER_SCRIPT_PLACEHOLDER, common_conf.MULTILAUNCHER_SCRIPTS_FOLDER)
                return os.system(cmd)
        except Exception as e:
            logger.error("Error while running " + cmd + ": " + str(e))

    def execute(self, message=''):
        """dispatch and execute message

        ``message``: message from topic
        """
        prefix = common_conf.MESSAGE_PREFIX_KEY
        for launcher in self.__launchers:
            if message.__contains__(prefix + ':' + launcher.start_message):
                self.__start_launcher(launcher)

            if message.__contains__(prefix + ':' + launcher.stop_message):
                self.__stop_launcher(launcher)


    def close(self):
        """rstop alla launchers
        """
        if common_conf.ON_EXIT_STOP_ALL:
            for launcher in self.launchers:
                self.__stop_launcher(launcher)


class Listener:
    """ Listener is a base class used to forward received message to Manager
    """
    @property
    def manager(self) -> Manager:
        return self.__manager

    @manager.setter
    def manager(self, value):
        self.__manager = value

    def run(self):
        pass

    def close(self):
        pass



