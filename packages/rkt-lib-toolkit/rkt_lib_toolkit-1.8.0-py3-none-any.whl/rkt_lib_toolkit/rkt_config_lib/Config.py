import os
import yaml

try:
    from rkt_logger_lib.Logger import Logger
except ImportError:
    from rkt_lib_toolkit.rkt_logger_lib.Logger import Logger

try:
    from rkt_tool_lib.Tool import Tool, Singleton
except ImportError:
    from rkt_lib_toolkit.rkt_tool_lib.Tool import Tool, Singleton


class Config(metaclass=Singleton):
    """
    Basic PyYaml wrapper
    add custom logger, list of file need to be load

    """
    __slots__ = ["_me", "_logger", "_tool", "_skills_file", "data"]

    def __init__(self) -> None:
        self._me = self.__class__.__name__
        self._logger = Logger(caller_class=self._me)
        self._logger.set_logger(caller_class=self._me)
        self._tool = Tool()
        self.data = {}

    def get_data(self, needed_file: str = "", _config_dir: str = "config", create_if_not_exist: bool = False) -> None:
        """
        Load all file in 'config_dir' and get data in dict formatted as : {"basename_1": <VALUE_1>, ...}
        """
        config_dir = self._tool.get_dir(_config_dir)

        if (not config_dir or not os.path.exists(config_dir)) and create_if_not_exist:
            os.makedirs(_config_dir, exist_ok=True)

        if needed_file:
            filename = os.path.basename(needed_file).split(".")[0]
            with open(f"{config_dir}{needed_file}", "r", encoding='utf8') as nf:
                self._logger.add(level="info", caller=self._me, message=f"Load '{filename}' file ...")
                self.data[filename] = yaml.load(nf, Loader=yaml.FullLoader)
        else:
            for file in os.listdir(config_dir):
                try:
                    (filename, ext) = os.path.basename(file).split(".")
                except ValueError:
                    continue
                if ext in ["yml", "yaml"] and filename not in self.data.keys():
                    with open(f"{config_dir}{file}", "r", encoding='utf8') as f:
                        self._logger.add(level="info", caller=self._me, message=f"Load '{filename}' file ...")
                        self.data[filename] = yaml.load(f, Loader=yaml.FullLoader)
