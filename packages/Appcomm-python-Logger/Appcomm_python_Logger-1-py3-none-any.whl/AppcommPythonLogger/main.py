from elasticsearch import Elasticsearch
from ftplib import FTP, FTP_TLS
import logging
import os
import socket
from datetime import datetime
from sqlalchemy import create_engine, text
import json
import sys
import ssl

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages based on log level."""
    COLORS = {
        'DEBUG': '\033[94m',      # Blue
        'INFO': '\033[92m',       # Green
        'NOTICE': '\033[96m',     # Cyan
        'WARNING': '\033[93m',    # Yellow
        'ERROR': '\033[91m',      # Red
        'CRITICAL': '\033[95m',   # Magenta
        'ALERT': '\033[35m',      # Purple
        'EMERGENCY': '\033[41m'   # Red background
    }
    RESET = '\033[0m'

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        log_message = super().format(record)
        return f"{log_color}{log_message}{self.RESET}"

class DatabaseHandler(logging.Handler):
    """Custom logging handler to save log records to a database."""
    def __init__(self, db_config):
        super().__init__()
        self.engine = self._initialize_db(db_config)

    def _initialize_db(self, db_config):
        """Parse the database configuration and initialize a connection."""
        db_type = db_config['driver']
        if db_type == 'sqlite':
            connection_string = f"sqlite:///{db_config['name']}"
        elif db_type in ['mysql', 'mariadb']:
            connection_string = (
                f"mysql+pymysql://{db_config['username']}:{db_config['password']}@"
                f"{db_config['host']}:{db_config.get('port', 3306)}/{db_config['name']}"
            )
        elif db_type == 'postgresql':
            connection_string = (
                f"postgresql+psycopg2://{db_config['username']}:{db_config['password']}@"
                f"{db_config['host']}:{db_config.get('port', 5432)}/{db_config['name']}"
            )
        elif db_type == 'oracle':
            service_name = db_config.get('service_name')
            connection_string = (
                f"oracle+cx_oracle://{db_config['username']}:{db_config['password']}@"
                f"{db_config['host']}:{db_config.get('port', 1521)}/?service_name={service_name}"
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        engine = create_engine(connection_string)
        self._create_table(engine)
        return engine

    def _create_table(self, engine):
        """Create the logs table if it doesn't exist."""
        try:
            with engine.connect() as conn:
                conn.execute(text(''' 
                    CREATE TABLE IF NOT EXISTS logs (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP,
                        host VARCHAR(255),
                        level VARCHAR(50),
                        message TEXT
                    )
                '''))
                conn.commit()
        except Exception as e:
            print(f"Failed to create logs table: {e}")

    def emit(self, record):
        """Write a log record to the database."""
        try:
            log_entry = {
                'timestamp': datetime.now(),
                'host': socket.gethostname(),
                'level': record.levelname,
                'message': record.getMessage()
            }
            with self.engine.connect() as conn:
                conn.execute(text(''' 
                    INSERT INTO logs (timestamp, host, level, message)
                    VALUES (:timestamp, :host, :level, :message)
                '''), log_entry)
                conn.commit()
        except Exception as e:
            print(f"Failed to write log to the database: {e}")

class ElasticsearchHandler(logging.Handler):
    def __init__(self, es_config):
        super().__init__()
        self.es = self._initialize_es(es_config)
        self.index_name = es_config.get('index', 'logs')

    def _initialize_es(self, es_config):
        context = ssl.create_default_context()
        context.check_hostname = False  
        context.verify_mode = ssl.CERT_NONE  

        es = Elasticsearch(
            hosts=[{'host': es_config['host'], 'port': es_config['port'], 'scheme': es_config['scheme']}],
            http_auth=(es_config.get('username'), es_config.get('password')),
            verify_certs=False, 
            ssl_context=context  
        )
        print(f"Initialized Elasticsearch client with {es_config['host']}:{es_config['port']}")
        return es

    def emit(self, record):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'host': socket.gethostname(),
            'level': record.levelname,
            'message': record.getMessage(),
        }
        try:
            self.es.index(index=self.index_name, document=log_entry)
        except Exception as e:
            print(f"Failed to write log to Elasticsearch: {e}")

class FTPHandler(logging.Handler):
    """Custom logging handler to upload log files to an FTP server."""
    def __init__(self, ftp_config, log_file_path):
        super().__init__()
        self.ftp_config = ftp_config
        self.log_file_path = log_file_path

    def _connect(self):
        """Establish an FTP connection."""
        if self.ftp_config.get('use_tls', False):
            ftp = FTP_TLS()
            ftp.connect(self.ftp_config['host'], self.ftp_config.get('port', 21))
            ftp.login(self.ftp_config['username'], self.ftp_config['password'])
            ftp.prot_p()  # Secure the data channel
        else:
            ftp = FTP()
            ftp.connect(self.ftp_config['host'], self.ftp_config.get('port', 21))
            ftp.login(self.ftp_config['username'], self.ftp_config['password'])
        return ftp

    def emit(self, record):
        """Upload the log file to the FTP server."""
        try:
            ftp = self._connect()
            with open(self.log_file_path, 'rb') as log_file:
                remote_path = f"{self.ftp_config.get('remote_dir', '/')}/{os.path.basename(self.log_file_path)}"
                ftp.storbinary(f"STOR {remote_path}", log_file)
            ftp.quit()
        except Exception as e:
            print(f"Failed to upload log file to FTP: {e}")


class Logger:
    def __init__(self, log_dir='./logs', db_configs=None, ftp_config=None):
        os.makedirs(log_dir, exist_ok=True)

        self.hostname = socket.gethostname()
        self.log_file = os.path.join(log_dir, "python.log")
        self.logger = logging.getLogger('Appcomm_python_Logger')
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(logging.Formatter(
            f'[%(asctime)s] [{self.hostname}] - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter(
            f'[%(asctime)s] [{self.hostname}] - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(console_handler)

        if ftp_config:
            ftp_handler = FTPHandler(ftp_config, self.log_file)
            self.logger.addHandler(ftp_handler)

        if db_configs:
            for db_config in db_configs:
                handler = self._initialize_handler(db_config)
                if handler:
                    self.logger.addHandler(handler)

        self.add_custom_levels()

    def _initialize_handler(self, db_config):
        try:
            db_type = db_config['driver']
            if db_type == 'elasticsearch':
                return ElasticsearchHandler(db_config)
            else:
                return DatabaseHandler(db_config)
        except Exception as e:
            print(f"Error initializing handler for {db_config['driver']}: {e}")
            return None

    def add_custom_levels(self):
        """Define custom logging levels."""
        logging.addLevelName(60, "EMERGENCY")
        logging.addLevelName(55, "ALERT")
        logging.addLevelName(25, "NOTICE")

        def emergency(self, message, *args, **kwargs):
            if self.isEnabledFor(60):
                self._log(60, message, args, **kwargs)

        def alert(self, message, *args, **kwargs):
            if self.isEnabledFor(55):
                self._log(55, message, args, **kwargs)

        def notice(self, message, *args, **kwargs):
            if self.isEnabledFor(25):
                self._log(25, message, args, **kwargs)

        logging.Logger.emergency = emergency
        logging.Logger.alert = alert
        logging.Logger.notice = notice

    @classmethod
    def setup_from_command_line(cls):
        """Initialize the Logger using command-line arguments."""

        if len(sys.argv) < 3:
            print("Usage: script.py --db <db_type> --log-dir <log_dir> --config <config_file>")
            sys.exit(1)

        db_types = []
        log_dir = './logs'
        config_file = None

        for i, arg in enumerate(sys.argv):
            if arg == '--db':
                db_types = sys.argv[i + 1].split(',')
            elif arg == '--log-dir':
                log_dir = sys.argv[i + 1]
            elif arg == '--config':
                config_file = sys.argv[i + 1]

        if not config_file:
            print("Error: --config argument is required.")
            sys.exit(1)

        try:
            with open(config_file, 'r') as file:
                database_configs = json.load(file)
        except FileNotFoundError:
            print(f"Error: The file {config_file} was not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: The file {config_file} is not a valid JSON file.")
            sys.exit(1)

        db_configs = []
        ftp_config = None

        for db_type in db_types:
            if db_type == 'ftp':
                ftp_config = database_configs.get('ftp')
                if not ftp_config:
                    print("Warning: No FTP configuration found in the provided JSON file.")
            else:
                db_config = database_configs.get(db_type)
                if db_config:
                    db_configs.append(db_config)
                else:
                    print(f"Warning: No configuration found for {db_type} in the provided JSON file.")

        return cls(log_dir=log_dir, db_configs=db_configs, ftp_config=ftp_config)

    def emergency(self, message):
        self.logger.emergency(message)

    def alert(self, message):
        self.logger.alert(message)

    def critical(self, message, exc=None):
        self.logger.critical(message, exc_info=exc)

    def error(self, message, exc=None):
        self.logger.error(message, exc_info=exc)

    def warning(self, message):
        self.logger.warning(message)

    def notice(self, message):
        self.logger.notice(message)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

if __name__ == "__main__":
    logger = Logger.setup_from_command_line()
    logger.info("Logger initialized successfully.")
