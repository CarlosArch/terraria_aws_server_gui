from configparser import ConfigParser

CONFIGURATION_FILE = 'config/config.ini'

CONFIG = ConfigParser()
CONFIG.read(CONFIGURATION_FILE)

DEFAULTS = {
    'server' : {'key_path' : 'place_in_config.pem',
                'server_dns' : 'ec2-public-ipv4-address.compute-1.amazonaws.com'},
    'world' : {'world_name' : 'TerrariaWorld'},
}

def save_config():
    with open(CONFIGURATION_FILE, 'w') as f:
        CONFIG.write(f)

def check_if_complete():
    for section, options in DEFAULTS.items():
        if section not in CONFIG.sections():
            CONFIG.add_section(section)
        for option, value in options.items():
            if option not in CONFIG.options(section):
                CONFIG.set(section, option, value)
    save_config()

check_if_complete()