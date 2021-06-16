import os
import logging
import yaml


app_name = 'diaman'
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AppConfig(metaclass=Singleton):
    """Holds all application configuration: credentials, logging, preprocessing."""
    # config filepaths
    _logging_conf_filepath = os.path.join(dir_path, 'logging.conf.yml')

    def __init__(self, app_name=app_name):
        self._prepare_logging()
        logger = logging.getLogger()
        logger.info("============================================================")

    def _prepare_logging(self):
        """
        Logging configuration.

        First part is a classic console + file logging. The file is a timebased
        rotating file. All this is configured in config-store/logging.conf.yml.

        Second part is the SentryHandler. Because of the credentials used to log
        to the appropriate Sentry Project, this part requires an 'application.yml'
        file. Normally, it is a symlink to one of the actual conffiles:

        - development.yml
        - preproduction.yml
        - production.yml

        Those files all have different credentials.
        """
        # create log dir
        try:
            log_dir_path = os.path.join(os.environ['REPO'], 'log')
            if not os.path.exists(log_dir_path):
                os.makedirs(log_dir_path)
        except FileExistsError:
            pass
        import logging.config
        with open(self._logging_conf_filepath) as f:
            dict_conf = yaml.load(f.read(), Loader=yaml.FullLoader)
            for k, v in dict_conf["handlers"].items():
                if v.get('filename', None):
                    v['filename'] = os.path.join(os.environ['REPO'], v.get('filename'))
            logging.config.dictConfig(dict_conf)
