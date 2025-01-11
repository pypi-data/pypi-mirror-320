import os
from configparser import ConfigParser
from pathlib import Path
from urllib.parse import urljoin

from autowork_cli.common.config.ConfigModel import ConfigModel
from autowork_cli.common.lang.dictclass import DictClass
from autowork_cli.common.lang.singleton import SingletonMeta

CONFIG_PATH = Path.home().joinpath(".autowork/config.ini")


def set_config_file_path(path):
    global CONFIG_PATH
    CONFIG_PATH = path


def get_config_file_path():
    global CONFIG_PATH
    return CONFIG_PATH


class LoginConfig(ConfigModel):

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = get_config_file_path()
        self.config_path = config_path
        self.config = LoginConfig.init_config(config_path)
        self.data = dict()
        for section in self.config.sections():
            d = dict()
            for k, v in self.config.items(section):
                d[k] = v
            self.data[section] = DictClass(d)

    @staticmethod
    def init_config(config_path):
        # allow_no_value设置为True以支持配置文件中添加注释
        config = ConfigParser(allow_no_value=True)
        # 配置文件内容区分大小写
        config.optionxform = lambda option: option
        config.read(config_path, encoding='utf-8')
        return config

    def __getattr__(self, item):
        if item in ["config", "data", "config_path"]:
            return object.__getattribute__(self, item)
        if item not in self.data:
            self.data[item] = DictClass()
        return self.data[item]

    def get(self, item) -> any:
        return self.__getattr__(item)

    def save(self, path=None):
        if path is None:
            path = self.config_path

        config = ConfigParser(allow_no_value=True)
        config.optionxform = lambda option: option
        for k in self.data:
            config[k] = self.data[k]

        dir_path = Path(path).parent.resolve()
        Path(dir_path).mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf8') as configfile:
            config.write(configfile)


    def set_product(self, product_name):
        self.get_global_config().PRODUCT = product_name

    def get_product(self):
        return self.get_global_config().get("PRODUCT")

    def set_env(self, env):
        self.get_global_config().ENV = env

    def get_env(self):
        return self.get_global_config().get("ENV")

    def set_other_url(self, url):
        product_env = self.get_product_env_str()
        if product_env not in self.data:
            self.data[product_env] = DictClass()
        self.data[product_env]['URL'] = url

    def get_other_url(self):
        product_env = self.get_product_env_str()
        if product_env not in self.data:
            self.data[product_env] = DictClass()
        api = "/fast_app" if self.get_product() == "FASTAPP" else "/cybotron-client"
        return urljoin(self.data[product_env].get('URL'), api)

    def get_other_domain_url(self):
        product_env = self.get_product_env_str()
        if product_env not in self.data:
            self.data[product_env] = DictClass()
        return self.data[product_env].get('URL')

    def set_debug(self, debug):
        self.get_global_config().DEBUG = debug

    def get_debug(self):
        return self.get_global_config().get("DEBUG")

    def get_global_config(self) -> DictClass:
        if "GLOBAL_CONFIG" not in self.data:
            self.data["GLOBAL_CONFIG"] = DictClass()
        return self.data["GLOBAL_CONFIG"]

    def get_dev_apps(self):
        return self.get_global_config().get("DEV_APPS")

    def set_dev_apps(self, dev_apps):
        self.get_global_config().DEV_APPS = dev_apps

    def set_api_key(self, api_key):
        product_env = self.get_product_env_str()
        if product_env not in self.data:
            self.data[product_env] = DictClass()
        self.data[product_env]['API_KEY'] = api_key

    def get_api_key(self):
        product_env = self.get_product_env_str()
        if product_env not in self.data:
            self.data[product_env] = DictClass()
        return self.data[product_env].get('API_KEY')

    def set_tenant_id(self, tenant_id):
        self.get_global_config().TENANT_ID = tenant_id

    def get_tenant_id(self):
        return self.get_global_config().get("TENANT_ID")

    def set_computer_name(self, computer_name):
        self.get_global_config().COMPUTER_NAME = computer_name

    def get_computer_name(self):
        return self.get_global_config().get("COMPUTER_NAME")

    def get_product_env_str(self):
        product = self.get_product()
        env = self.get_env()
        return f"{product}-{env}"

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return self.__str__()


DefaultLoginConfig = LoginConfig()
