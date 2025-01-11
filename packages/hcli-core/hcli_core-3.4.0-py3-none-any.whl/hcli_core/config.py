import sys
import os
import stat
import importlib
import inspect
from configparser import ConfigParser
from threading import Lock
from hcli_core import logger
import signal
import atexit

log = logger.Logger("hcli_core")


class ServerContext:
    _context = {}
    _lock = Lock()

    @classmethod
    def set_current_server(cls, server_type):
        with cls._lock:
            cls._context['current_server'] = server_type

    @classmethod
    def get_current_server(cls):
        with cls._lock:
            return cls._context.get('current_server', 'core')

    @classmethod
    def set_current_user(cls, username):
        with cls._lock:
            cls._context['current_user'] = username

    @classmethod
    def get_current_user(cls):
        with cls._lock:
            return cls._context.get('current_user', None)

class Config:
    _instances = {}       # Dictionary to store named instances
    _instance_locks = {}  # Dictionary to store locks for each named instance
    _global_lock = Lock() # Lock for managing instance creation

    # Get management port from config file if explicitly configured, else None.
    @classmethod
    def get_management_port(cls, config_path=None):
        with cls._global_lock:
            if not config_path:
                config_path = os.path.join(os.path.dirname(inspect.getfile(lambda: None)), "auth/cli/credentials")

            try:
                parser = ConfigParser(interpolation=None)
                with open(config_path, 'r') as config_file:
                    parser.read_file(config_file)

                    if parser.has_section("config") and parser.has_option("config", "mgmt.port"):
                        try:
                            port = int(parser.get("config", "mgmt.port"))
                            if 1 <= port <= 65536:
                                return port
                            log.warning(f"Invalid management port value: {port}")
                        except ValueError:
                            log.warning("Invalid management port configuration")

                return None
            except Exception as e:
                log.warning(f"Error reading management port configuration: {e}")
                return None

    # Get management root aggregation cue from config file if explicitly configured, else None.
    @classmethod
    def get_core_root(cls, config_path=None):
        with cls._global_lock:
            if not config_path:
                config_path = os.path.join(os.path.dirname(inspect.getfile(lambda: None)), "auth/cli/credentials")

            try:
                parser = ConfigParser(interpolation=None)
                with open(config_path, 'r') as config_file:
                    parser.read_file(config_file)

                    if parser.has_section("config") and parser.has_option("config", "core.root"):
                        try:
                            root = parser.get("config", "core.root")
                            if root == 'aggregate' or root == 'management':
                                return root
                            log.warning(f"Invalid core root value: {root}")
                        except ValueError:
                            log.warning("Invalid core root configuration")

                return None
            except Exception as e:
                log.warning(f"Error reading management root configuration: {e}")
                return None

    def __new__(cls, name=None):
        # If no name provided, get it from context
        if name is None:
            name = ServerContext.get_current_server()

        # Create lock for this instance name if it doesn't exist
        with cls._global_lock:
            if name not in cls._instance_locks:
                cls._instance_locks[name] = Lock()

        # Check if instance exists, if not create it
        if name not in cls._instances:
            with cls._instance_locks[name]:  # Thread-safe instance creation
                if name not in cls._instances:  # Double-checked locking
                    instance = super(Config, cls).__new__(cls)
                    # Initialize instance attributes
                    instance.name = name
                    instance.root = os.path.dirname(inspect.getfile(lambda: None))
                    instance.sample = instance.root + "/sample"
                    instance.hcli_core_manpage_path = instance.root + "/data/hcli_core.1"
                    instance.template = None
                    instance.plugin_path = instance.root + "/cli"
                    instance.cli = None
                    instance.default_config_file_path = instance.root + "/auth/cli/credentials"
                    instance.config_file_path = None
                    instance.auth = True
                    instance.log = logger.Logger(f"hcli_core")
                    instance.mgmt_credentials = 'local'
                    instance.core_root = None
                    if name == 'management':
                        instance.mgmt_port = 9000
                    cls._instances[name] = instance

        return cls._instances[name]

    @classmethod
    def get_instance(cls, name="core"):
        """Get a named instance of the Config class."""
        return cls(name)

    @classmethod
    def list_instances(cls):
        """List all created configuration instances."""
        return list(cls._instances.keys())

    def parse_configuration(self):
        try:
            with open(self.config_file_path, 'r') as config_file:
                parser = ConfigParser(interpolation=None)
                parser.read_file(config_file)

                if parser.has_section("config"):
                    for section_name in parser.sections():
                        if section_name == "config":
                            for name, value in parser.items("config"):
                                if name == "core.auth":
                                    if self.name == 'core':
                                        if value != "False" and value != "True":
                                            log.warning("Unsupported core auth value: " + str(value) + ". Enabling authentication.")
                                            self.auth = True
                                        else:
                                            if value.lower() == 'true':
                                                self.auth = True
                                            elif value.lower() == 'false':
                                                self.auth = False
                                        log.info("Core Auth: " + str(self.auth))
                                elif name == "mgmt.port":
                                    if self.name == 'management':
                                        port = int(value)
                                        valid = (1 <= port <= 65536)
                                        if not valid:
                                            log.warning("Unsupported management port value: " + str(value) + ". Defaulting to 9000.")
                                            self.mgmt_port = 9000
                                        else:
                                            self.mgmt_port = port
                                            log.info("Management Port: " + str(self.mgmt_port))
                                elif name == "mgmt.credentials":
                                        mgmt_credentials = value
                                        valid = (mgmt_credentials == 'local' or mgmt_credentials == 'remote')
                                        if not valid:
                                            log.warning("Unsupported credentials management mode: " + str(value) + ". Defaulting to local.")
                                            self.mgmt_credentials = 'local'
                                        else:
                                            self.mgmt_credentials = value
                                            log.info("Credentials management: " + str(self.mgmt_credentials))
                                elif name == "core.root":
                                        core_root = value
                                        valid = (core_root == 'aggregate' or core_root == 'management')
                                        if not valid:
                                            log.warning("Unsupported core root override: " + str(value) + ". Defaulting to None.")
                                            self.core_root = None
                                        else:
                                            self.core_root = value
                                            log.info("Core root override: " + str(self.core_root))
                            if self.name == 'management':
                                log.info("Management Auth: " + str(self.auth))
                            if self.name == 'management' and not parser.has_option("config", "mgmt.port"):
                                log.info(f"Default Management Port: {self.mgmt_port}")
                else:
                    log.critical("No [config] configuration available for " + self.config_file_path + ".")
        except Exception as e:
            log.critical(f"Unable to load configuration: {str(e)}")
            assert False

    def set_config_path(self, config_path):
        if config_path:
            self.config_file_path = config_path
            self.log.info(f"Custom configuration for '{self.name}':")
        else:
            self.config_file_path = self.default_config_file_path
            self.log.warning(f"Default configuration for '{self.name}':")
        self.log.info(self.config_file_path)

        if not self.is_600(self.config_file_path):
            self.log.critical("The credentials file's permissions should be set to 600 (e.g. chmod 600 credentials).")

    def parse_template(self, t):
        self.template = t

    def set_plugin_path(self, p):
        if p is not None:
            self.plugin_path = p

        try:
            # Always ensure both paths are available
            plugin_dir = os.path.dirname(self.plugin_path)
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)
            if self.plugin_path not in sys.path:
                sys.path.insert(0, self.plugin_path)

            log.info(f"Loading CLI module for {self.name} from path: {self.plugin_path}.")

            # Load the module
            self._cli_module = importlib.import_module("cli", self.plugin_path)

            # Verify CLI class exists
            if not hasattr(self._cli_module, 'CLI'):
                raise ImportError(f"No CLI class found in module for {self.name}.")

            log.info(f"Successfully loaded CLI plugin for {self.name}.")

            # Test instantiation
            test_cli = self._cli_module.CLI(['test'], None)
            log.info(f"Successfully verified CLI class instantiation for {self.name}.")

        except Exception as e:
            self.log.error(f"Failed to load CLI plugin from {self.plugin_path}: {str(e)}")
            raise

    def set_plugin_path(self, p):
        if p is not None:
            self.plugin_path = p

        try:
            # Clear any existing 'cli' module from cache
            if 'cli' in sys.modules:
                del sys.modules['cli']

            plugin_dir = os.path.dirname(self.plugin_path)
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)
            if self.plugin_path not in sys.path:
                sys.path.insert(0, self.plugin_path)

            log.debug(f"Loading CLI for {self.name}.")
            log.debug(f"Plugin path: {self.plugin_path}.")
            log.debug(f"sys.path: {sys.path}.")

            # Use a unique module name for each CLI
            module_name = f"cli_{self.name}"
            cli_path = os.path.join(self.plugin_path, 'cli.py')

            log.debug(f"Loading from: {cli_path}")
            spec = importlib.util.spec_from_file_location(module_name, cli_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._cli_module = module
            log.debug(f"Loaded module from: {module.__file__}.")

            log.info(f"Successfully loaded CLI plugin for {self.name}.")
        except Exception as e:
            log.error(f"Failed to load CLI plugin from {self.plugin_path}: {str(e)}")
            raise

    # Return the CLI class itself, not the module
    @property
    def cli(self):
        if hasattr(self, '_cli_module'):
            if hasattr(self._cli_module, 'CLI'):
                return getattr(self._cli_module, 'CLI')
        return None

    @cli.setter
    def cli(self, value):
        self._cli_module = value

    def is_600(self, filepath):
        mode = os.stat(filepath).st_mode & 0o777

        # Print actual permissions and platform for debugging
        log.debug(f"Platform: {sys.platform}")
        log.info(f"Credentials file permissions (octal): {oct(mode)}")

        # 0o600 = rw------- (read/write for owner only)
        is_user_rw = bool(mode & 0o600)  # User has read and write
        is_other_none = (mode & 0o177) == 0  # No permissions for group/others

        return is_user_rw and is_other_none

    def __str__(self):
        return f"{self.name}"
