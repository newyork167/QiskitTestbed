from configparser import ConfigParser
from Metaclass.ThreadSafeSingleton import ThreadSafeSingleton
import pathlib
import os


class NY167Config(metaclass=ThreadSafeSingleton):
    config: ConfigParser = None

    def __init__(self, config_path=f"{pathlib.Path(__file__).parent.absolute()}{os.sep}config.ini"):
        print(f"Loading config from {config_path}")
        self.config = ConfigParser()
        self.config.read(config_path)

    def get(self, section, option):
        return self.config.get(section=section, option=option)

    def get_boolean(self, section: str, option: str) -> bool:
        return self.config.getboolean(section=section, option=option)

    def get_int(self, section: str, option: str) -> int:
        return self.config.getint(section=section, option=option)

    def get_float(self, section: str, option: str) -> float:
        return self.config.getfloat(section=section, option=option)

    def get_as_array(self, section: str, option: str, delimiter: str = ',') -> []:
        return [str(x).strip() for x in self.config.get(section=section, option=option).split(delimiter)]

    def has_option(self, section, option):
        return self.config.has_option(section=section, option=option)
