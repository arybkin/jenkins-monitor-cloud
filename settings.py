import json
import os

APPENDIX = "JENKINS_MONITOR_"
JENKINS_LIST = f"{APPENDIX}JENKINS_LIST"
CONFIG_FILE = "settings.json"

CONFIG_POSTGRES_ADDRESS = "Postgres_Address"
CONFIG_POSTGRES_PORT = "Postgres_Port"
CONFIG_POSTGRES_USERNAME = "Postgres_Username"
CONFIG_POSTGRES_PASSWORD = "Postgres_Password"

CONFIG_POSTGRES_DB = "Postgres_Database"
CONFIG_JENKINS_URL = "Jenkins_Url"
CONFIG_JENKINS_USERNAME = "Jenkins_Username"
CONFIG_JENKINS_PASSWORD = "Jenkins_Password"

CONFIGS = dict()


def init_configs():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def build_allowed_configs(available_list):
    if os.environ.get("JENKINS_LIST"):
        available_list = os.environ.get("JENKINS_LIST")

    config_list = []
    for config in available_list:
        config_list.append(Configuration(config))

    return config_list


class ConfigurationBase:
    postgres_address = ""
    postgres_port = ""
    postgres_username = ""
    postgres_password = ""

    def __init__(self):
        self.config = init_configs()
        section = "Base"
        self.postgres_address = self.get_config(CONFIG_POSTGRES_ADDRESS, section)
        self.postgres_port = self.get_config(CONFIG_POSTGRES_PORT, section)
        self.postgres_username = self.get_config(CONFIG_POSTGRES_USERNAME, section)
        self.postgres_password = self.get_config(CONFIG_POSTGRES_PASSWORD, section)

    def get_config(self, config_name, section):
        target_value = self.__get_os_var(config_name, section)
        if not target_value:
            target_value = self.__get_config_var(config_name, section)

        if not target_value:
            raise Exception(f"There is no key:{config_name} in section {section}")

        return target_value

    def __get_config_var(self, key: str, name: str):
        print(self.config)
        print(self.config.get(name))
        print(self.config.get(name).get(key))
        return self.config.get(name).get(key)

    @staticmethod
    def __get_os_var(key: str, name: str):
        if name:
            var = f"{APPENDIX}{name.upper()}_{key.upper()}"
            return os.environ.get(var)
        var = f"{APPENDIX}{key.upper()}"
        return os.environ.get(var)


class Configuration(ConfigurationBase):
    jenkins_url = ""
    jenkins_username = ""
    jenkins_password = ""
    db_name = ""
    name = ""

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.jenkins_url = self.get_config(CONFIG_JENKINS_URL, name)
        self.jenkins_username = self.get_config(CONFIG_JENKINS_USERNAME, name)
        self.jenkins_password = self.get_config(CONFIG_JENKINS_PASSWORD, name)
        self.db_name = self.get_config(CONFIG_POSTGRES_DB, name)
