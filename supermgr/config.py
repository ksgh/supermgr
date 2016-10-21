import ConfigParser
import os.path

'''
    This is usually the default for supervisord, although by default it is also commented out
'''
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 9001

def get_config(use_file=None):
    config = ConfigParser.ConfigParser()

    if use_file:
        config_files = (use_file,)
    else:
        # @TODO: move this to a more accessible place
        config_files = (
            '/etc/supervisord.conf',
            os.path.join(os.path.expanduser('~'), '.supervisord'),
            '/etc/supervisor.d/inet_http_server.conf'
        )

    for f in config_files:
        if not os.path.isfile(f):
            continue
        config.read(f)

        try:
            conn = config.get('inet_http_server', 'port')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            continue

        if conn:
            hp = conn.split(':')
            try:
                return {'host': hp[0], 'port': hp[1]}
            except IndexError:
                return {}

    return {'host': DEFAULT_HOST, 'port': DEFAULT_PORT}
