import os
import pytest
from mock import patch
from settings import ConfigurationBase, CONFIG_FILE, APPENDIX


@patch("settings.CONFIG_FILE", "tests/unit/settings.json")
def test_exist_json():
    ConfigurationBase()
    pass


# def test_not_exist_json():
#     with pytest.raises(FileNotFoundError):
#         ConfigurationBase()


@patch("settings.CONFIG_FILE", "tests/unit/settings.json")
def test_support_env_param_CONFIG_POSTGRES_ADDRESS():
    config_postgres_adderess = (APPENDIX + "BASE" + "config_postgres_adderess").upper()
    os.environ[APPENDIX + "BASE" +"_POSTGRES_ADDRESS"] = config_postgres_adderess
    conf = ConfigurationBase()
    assert(conf.postgres_address, config_postgres_adderess)


