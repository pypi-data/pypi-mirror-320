import os
import sys
import yaml
from pathlib import Path

from improvelib.initializer.cli import CLI
from improvelib.utils import str2bool, cast_value

BREAK = os.getenv("IMPROVE_DEV_DEBUG", None)


class Config:
    """Class to handle configuration files."""

    config_sections = ['DEFAULT', 'Preprocess', 'Train', 'Infer']

    def __init__(self) -> None:
        """Initialize the Config class with default settings."""
        # Set up logging format
        FORMAT = '%(levelname)s %(name)s %(asctime)s:\t%(message)s'
        logging.basicConfig(format=FORMAT)

        # Required configuration parameters
        required = ["input_dir", "output_dir", "log_level", 'config_file']

        # Initialize instance variables
        self.params = {}
        self.file = None  # Path to the configuration file
        self.logger = logging.getLogger('Config')
        self.log_level = os.getenv("IMPROVE_LOG_LEVEL", logging.INFO)
        self.logger.setLevel(self.log_level)

        self.required = required
        self.config = configparser.ConfigParser()
        self.cli = CLI()
        self.input_dir = None
        self.output_dir = None
        self.params = {}
        self._options = {}

        # Set default directories based on environment variables
        # Check if both CANDLE_DATA_DIR and IMPROVE_DATA_DIR are set in the environment
        if "CANDLE_DATA_DIR" in os.environ and "IMPROVE_DATA_DIR" in os.environ:
            # Ensure that both directories are identical; if not, log an error and raise an exception
            if not os.getenv('IMPROVE_DATA_DIR') == os.getenv("CANDLE_DATA_DIR"):
                self.logger.error(
                    "Found CANDLE_DATA_DIR and IMPROVE_DATA_DIR but they are not identical.")
                raise ValueError('Alias not identical')
            else:
                # If they are identical, set the default input directory in the config
                self.config.set("DEFAULT", "input_dir",
                                os.getenv("IMPROVE_DATA_DIR", "./"))

        # If only CANDLE_DATA_DIR is set, use it as the IMPROVE_DATA_DIR
        elif "CANDLE_DATA_DIR" in os.environ:
            os.environ["IMPROVE_DATA_DIR"] = os.environ["CANDLE_DATA_DIR"]

        # If IMPROVE_OUTPUT_DIR is not set, default it to IMPROVE_DATA_DIR or current directory
        if "IMPROVE_OUTPUT_DIR" not in os.environ:
            self.logger.debug('Setting output directory to default.')
            os.environ["IMPROVE_OUTPUT_DIR"] = os.environ.get(
                "IMPROVE_DATA_DIR", "./")

        # Set the default input and output directories in the config
        self.config.set("DEFAULT", "input_dir",
                        os.environ.get("IMPROVE_DATA_DIR", "./"))
        self.config.set("DEFAULT", "output_dir",
                        os.environ.get("IMPROVE_OUTPUT_DIR", "./"))

    def _add_option(self, name: str, option: dict) -> bool:
        """Add a command line option definition to _options.

        Args:
            name (str): The name of the option.
            option (dict): The option definition.

        Returns:
            bool: True if the option was added successfully, False otherwise.
        """
        # Validate option is a dictionary
        if not isinstance(option, dict):
            self.logger.error("Option %s is not a dictionary", name)
            sys.exit(1)

        # Ensure option name matches dictionary entry
        if "name" in option:
            if not name == option['name']:
                self.logger.error("Option name %s is not identical to name in dictionary %s", name, option['name'])
                sys.exit(1)
        elif not name == option['dest']:
            self.logger.error("Option name %s is not identical to name in dictionary %s", name, option['dest'])
            sys.exit(1)

        # Check for duplicate options
        if name in self._options:
            self.logger.error("Option %s is already defined. Skipping.", name)
            return False

        # Check for required keys in option
        if not all(k in option for k in ('name', 'type', 'default', 'help')):
            self.logger.warning("Option %s is missing required keys.", name)

        # Set default type and value if missing
        if "type" not in option:
            self.logger.error("Option %s is missing type. Setting to str.", name)
            option['type'] = str
        if "default" not in option:
            self.logger.error("Option %s is missing default. Setting to None.", name)
            option['default'] = None

        # Validate option type
        if option['type'] not in ['str', 'int', 'float', 'bool', 'str2bool', None, str, int, float, bool, str2bool]:
            self.logger.error("Unsupported type %s for option %s", option['type'], name)
            sys.exit(1)

        # Add option to _options
        self._options[name] = option
        return True

    def _update_options(self) -> bool:
        """Update _options with options from the command line (argparse).

        Returns:
            bool: True if options were updated successfully.
        """
        for action in self.cli.parser._actions:
            self._add_option(action.dest, action.__dict__)
        return True

    def _update_cli_defaults(self) -> bool:
        """Update command line defaults with values from _options.

        Returns:
            bool: True if CLI defaults were updated successfully.
        """
        # Get config file from command line
        config_file = self.cli.get_config_file()

        # Set self.file to config file if provided
        if config_file is not None:
            self.file = config_file
        else:
            self.logger.debug("No config file provided in command line arguments.")

        if self.file is None:
            self.logger.debug("No config file provided at all.")
            return False

        # Load the config file
        self.load_config()

        # Update CLI defaults from config file
        for section in self.config.sections():
            if self.section is None or self.section == section:
                for option in self.config.items(section):
                    print(option)
                    (key, value) = option
                    if key in self._options:
                        if 'nargs' in self._options[key] and \
                                self._options[key]['nargs'] and \
                                self._options[key]['nargs'] not in [None, 0, 1, "0", "1"]:
                            if BREAK:
                                # If the BREAK environment variable is set, trigger a breakpoint for debugging
                                breakpoint()
                            try:
                                # Attempt to convert the string value to a list using JSON decoding
                                value = json.loads(value)
                            except json.JSONDecodeError:
                                # Log an error if the conversion fails and exit the program
                                self.logger.error("Can't convert %s to list", value)
                                self.logger.critical(json.JSONDecodeError)
                                sys.exit(1)
                        elif 'type' in self._options[key]:
                            # Check the type of the option and convert the value accordingly
                            t = self._options[key]['type']
                            if t == 'str' or t == str:
                                value = str(value)
                            elif t == 'int' or t == int:
                                value = int(value)
                            elif t == 'float' or t == float:
                                value = float(value)
                            elif t == 'bool' or t == bool:
                                value = str2bool(value)
                            elif t == 'str2bool':
                                value = str2bool(value)
                            else:
                                self.logger.error("Unsupported type %s",
                                                  self._options[option[0]]['type'])
                                value = str(value)

                        self.cli.parser.set_defaults(**{key: value})

        return True

    def set_command_line_options(self, options: list = [], group: str = None) -> bool:
        """Set command line options.

        Args:
            options (list): A list of command line options.
            group (str, optional): The name of the argument group to add options to.

        Returns:
            bool: True if command line options were set successfully.
        """
        self.cli.set_command_line_options(options)
        self._update_options()
        return True

    def get_command_line_options(self) -> dict:
        """Get command line options.

        Returns:
            dict: A dictionary of parsed command line arguments.
        """
        self._update_cli_defaults()
        return self.cli.get_command_line_options()

    def load_config(self) -> None:
        """Load the configuration file."""
        if self.file and os.path.isfile(self.file):
            self.logger.info("Loading config from %s", self.file)
            self.config.read(self.file)
        else:
            self.logger.error("Can't load config from %s", str(self.file))
            self.config['DEFAULT'] = {}

    def save_parameter_file(self, file_name: str) -> None:
        """Save final parameters to a file.

        Args:
            file_name (str): The name of the file to save parameters to.
        """
        # Check if a file name is provided for saving parameters
        if file_name is None:
            # Log a warning if no file name is provided and exit the function
            self.logger.warning("No file name provided to save parameters.")
            return
        else:
            # Log the file name where parameters will be saved
            self.logger.debug("Saving parameters to %s", file_name)
            
            # Determine the path to save the file
            if os.path.isabs(file_name):
                # If the file name is an absolute path, use it directly
                path = file_name
            else:
                # If the file name is not absolute, construct the path using the output directory
                path = Path(self.output_dir, file_name)
                
                # Check if the directory exists, and create it if it doesn't
                if not Path(path.parent).exists():
                    self.logger.debug(
                        "Creating directory %s for saving config file.", path.parent)
                    Path(path.parent).mkdir(parents=True, exist_ok=True)

            # Open the file and write the parameters to it
            with path.open("w") as f:
                f.write(str(self.params)) 

    def save_config(self, file_name: str, config: configparser.ConfigParser = None) -> None:
        """Save the configuration to a file.

        Args:
            file_name (str): The name of the file to save the configuration to.
            config (configparser.ConfigParser, optional): The configuration to save. Defaults to None.
        """
        # Determine if the file name is an absolute path
        if os.path.isabs(file_name):
            # If absolute, write the configuration directly to the specified file
            with open(file_name, 'w') as out_file:
                self.config.write(out_file)
        else:
            # If not absolute, construct the path using the output directory
            path = Path(self.output_dir, file_name)
            
            # Check if the directory exists, and create it if it doesn't
            if not Path(path.parent).exists():
                self.logger.debug(
                    "Creating directory %s for saving config file.", path.parent)
                Path(path.parent).mkdir(parents=True, exist_ok=True)

        # Open the file and write the parameters to it
        with path.open("w") as f:
            f.write(str(self.params))

    def param(self, section: str = "DEFAULT", key: str = None, value: str = None) -> (str, str):
        """Get or set value for given option.

        Args:
            section (str, optional): The section name. Defaults to "DEFAULT".
            key (str, optional): The key name. Defaults to None.
            value (str, optional): The value to set. Defaults to None.

        Returns:
            tuple: A tuple containing the value and an error message, if any.
        """
        error = None

        # If a value is provided, attempt to set it in the specified section
        if value is not None:
            if self.config.has_section(section):
                self.config[section][key] = value
            else:
                error = "Unknown section " + str(section)
                self.logger.error(error)

        # Retrieve the value for the specified key in the section
        if self.config.has_option(section, key):
            value = self.config[section][key]
        else:
            error = "Can't find option " + str(key)
            self.logger.error(error)
            value = None

        return (value, error)

    def get_param(self, section: str = "DEFAULT", key: str = None) -> str:
        """Get value for given option.

        Args:
            section (str, optional): The section name. Defaults to "DEFAULT".
            key (str, optional): The key name. Defaults to None.

        Returns:
            str: The value of the option.
        """
        error = None

        # Check if the specified key exists in the given section
        if self.config.has_option(section, key):
            # Retrieve the value for the specified key
            value = self.config[section][key]
        else:
            # Log an error if the key is not found and set value to None
            error = "Can't find option " + str(key)
            self.logger.error(error)
            value = None

        return value

    def set_param(self, section: str = "DEFAULT", key: str = None, value: str = None) -> (str, str):
        """
        Set value for a given option. Gets or sets value in DEFAULT section if section is not provided.
        Allowed section names are: Preprocess, Train, and Infer.

        Args:
            section (str, optional): The section name. Defaults to "DEFAULT".
            key (str, optional): The key name. Defaults to None.
            value (str, optional): The value to set. Defaults to None.

        Returns:
            tuple: A tuple containing the value and an error message, if any.
        """
        msg = None

        # Check if a key is provided
        if key:
            # Ensure the section exists, create it if it doesn't
            if not self.config.has_section(section) and section != "DEFAULT":
                msg = "Unknown section " + str(section)
                self.logger.debug(msg)
                self.config[section] = {}

            # Set the value for the key in the section
            if value is None:
                value = ''

            self.logger.debug("Key:%s\tValue:%s", key, value)
            self.config[section][key] = str(value)
        else:
            msg = "Can't update config, empty key"
            self.logger.error(msg)
            return (None, msg)

        return (self.config[section][key], msg)
    

    def section_parameters(self, section=None) -> dict:
        """
        Return a dictionary of all options in the config file. If section
        is provided, return a dictionary of options in that section.
        TODO do really want of overload python's dict function?
        """
    
        params = {}
        sections = []

        if section:
            sections = [section]
        else:
            sections = self.config.sections()

        if section:
            # check if section exists
            if section in self.config:
                for i in self.config.items(section):
                    params[i[0]] = i[1]
            else:
                self.logger.error("Can't find section %s", section)

        else:
            for s in self.config.sections():
                params[s] = {}
                for i in self.config.items(s):
                    params[s][i[0]] = i[1]

        return params
    

    def check_required(self):
        """Check if all required parameters are set."""
        pass


    def _validate_parameters(self, params, required=None):
        """Validate parameters. Set types and check for required parameters."""

        if params is None:
            return

        for p in params:
            # check if type is set and convert to python type
            if 'type' in p:
                if p['type'] == 'str':
                    p['type'] = str
                elif p['type'] == 'int':
                    p['type'] = int
                elif p['type'] == 'float':
                    p['type'] = float
                elif p['type'] == 'bool':
                    p['type'] = bool
                elif p['type'] == 'str2bool':
                    p['type'] = str2bool
                else:
                    self.logger.error("Unsupported type %s", p['type'])
                    p['type'] = str


    def load_parameter_definitions(self, file, section=None):
        """
        Load parameters definitions from from a file. 
        Used if not passed as a list.
        """
        self.logger.debug("Loading parameters from %s", file)

        # Convert Path to string
        if file and isinstance(file, Path):
            file = str(file)

        if os.path.isfile(file):
            # check if yaml or json file and load
            params = None

            if file.endswith('.json'):
                with open(file, 'r') as f:
                    params = json.load(f)
            elif file.endswith('.yaml') or file.endswith('.yml'):
                with open(file, 'r') as f:
                    params = yaml.safe_load(f)
            else:
                self.logger.error("Unsupported file format")
            self._validate_parameters(params)
            return params
        else:
            print(isinstance(file, str))
            self.logger.critical("Can't find file %s", file)
            sys.exit(1)
            return None


    def validate_parameters(self, params, required=None):
        """Validate parameters."""
        pass


    def load_config_file(self, pathToModelDir=None, default_config=None):
        """
        Loads the configuration file. 
        """
        if self.input_dir and os.path.isdir(self.input_dir):

            # Set config file name
            if self.cli.args.config_file:
                self.file = self.cli.args.config_file
            else:
                # Make pathToModelDir and default_config same type. Possible types are: str, Path
                if isinstance(pathToModelDir, Path):
                    pathToModelDir = str(pathToModelDir)
                if isinstance(default_config, Path):
                    default_config = str(default_config)

                if pathToModelDir is not None:
                    if not pathToModelDir.endswith("/"):
                        pathToModelDir += "/"
                else:
                    pathToModelDir = "./"

                if default_config is not None:
                    if not os.path.abspath(default_config):
                        self.logger.debug(
                            "Not absolute path for config file. Should be \
                            relative to model directory")
                        self.file = pathToModelDir + default_config
                    else:
                        self.logger.warning("Default config not releative to \
                                            model directory. Using as is.")
                        self.file = default_config
                        
                else:
                    self.logger.warning("No default config file provided")

                self.logger.debug("No config file provided. Using default: %s", self.file)

            # Set full path for config
            if self.file and not os.path.abspath(self.file):
                self.logger.debug(
                    "Not absolute path for config file. Should be relative to input_dir")
                self.file = self.input_dir + "/" + self.file
                self.logger.debug("New file path: %s", self.file)

            # Load config if file exists
            if self.file and os.path.isfile(self.file):
                self.load_config()
            else:
                self.logger.warning("Can't find config file: %s", self.file)
                self.config[section] = {}
        else:
            self.logger.critical("No input directory: %s", self.input_dir)


    def ini2dict(self, section=None , flat=False) -> dict:
        """
        Return a dictionary of all options in the config file. If section is provided,
        return a dictionary of options in that section. If flat is True, return a flat
        dictionary without sections.
        """

        params = {}
        sections=[]

        if section :
            sections=[section]
        else:
            sections=self.config.sections()
        
        if section:
            # check if section exists
            if self.config.has_section(section):
                for i in self.config.items(section):
                    params[i[0]]=i[1]
            else:
                self.logger.error("Can't find section %s", section)

        else:
            if flat:
                for s in self.config.sections():
                    for i in self.config.items(s):
                        params[i[0]]=i[1]
            else:
                for s in self.config.sections():
                    params[s]={}
                    for i in self.config.items(s):
                        params[s][i[0]]=i[1]

        return params


    def dict(self, section=None) -> dict : # rename to ini2dict ; keep dict as alias
        """
        Return a dictionary of all options in the config file. If section is provided,
        return a dictionary of options in that section
        """
        return self.ini2dict(section=section)


    # Load command line definitions from a file
    def load_cli_parameters(self, file, section=None):
        """Load parameters from a file."""
        self.logger.debug("Loading parameters from %s", file)

        # Convert Path to string
        if file and isinstance(file, Path):
            file = str(file)

        if os.path.isfile(file):
            # check if yaml or json file and load
            params = None

            if file.endswith('.json'):
                with open(file, 'r') as f:
                    params = json.load(f)
            elif file.endswith('.yaml') or file.endswith('.yml'):
                with open(file, 'r') as f:
                    params = yaml.safe_load(f)
            else:
                self.logger.error("Unsupported file format")
            self._validate_parameters(params)
            return params
        else:
            print(isinstance(file, str))
            self.logger.critical("Can't find file %s", file)
            sys.exit(1)
            return None

    def update_defaults(self, cli_definitions: list = None, new_defaults: dict = None) -> list:
        """Update the default values for the command line arguments with the new defaults.

        Args:
            cli_definitions (list, optional): A list of command line definitions. Defaults to None.
            new_defaults (dict, optional): A dictionary of new default values. Defaults to None.

        Returns:
            list: A list of updated parameter definitions.
        """
        # Extract existing option names from the CLI parser
        existing_options = [o.lstrip('-') for o in self.cli.parser._option_string_actions]

        # Check if new defaults are provided
        if not new_defaults:
            self.logger.error("No new defaults provided.")
            return

        # Check if CLI definitions are provided
        if not cli_definitions:
            self.logger.error("No command line definitions provided.")
            return

        updated_parameters = []

        # Iterate over each entry in the CLI definitions
        for entry in cli_definitions:
            self.logger.debug("Updating " + str(entry))
            
            # Check if the entry name exists in the new defaults
            if entry['name'] in new_defaults:
                # Update the default value for the entry
                entry['default'] = new_defaults[entry['name']]
                
                # Handle entries with multiple arguments
                if "nargs" in entry:
                    try:
                        # Attempt to convert the default value to a list
                        entry['default'] = json.loads(new_defaults[entry['name']])
                    except json.JSONDecodeError:
                        self.logger.error("Can't convert %s to list", new_defaults[entry['name']])
                        self.logger.error(json.JSONDecodeError)
                
                # Handle entries with specific types
                elif "type" in entry:
                    if entry['type'] == bool:
                        entry['default'] = str2bool(entry['default'])
                    elif entry['type'] == int:
                        entry['default'] = int(entry['default'])
                    elif entry['type'] == str:
                        entry['default'] = str(entry['default'])
                    elif entry['type'] == float:
                        entry['default'] = float(entry['default'])
                else:
                    self.logger.error("No type provided for " + str(entry['name']))

                # Update the CLI parser defaults if the entry exists in existing options
                if entry['name'] in existing_options:
                    self.cli.parser.set_defaults(**{entry['name']: entry['default']})

            # Add the updated entry to the list of updated parameters
            updated_parameters.append(entry)
        
        return updated_parameters

    def update_cli_definitions(self, definitions: list = None) -> list:
        """Update the command line argument definitions with values from the config file.

        Args:
            definitions (list, optional): A list of command line definitions. Defaults to None.

        Returns:
            list: A list of updated parameter definitions.
        """
        # Retrieve the config file path from command line arguments
        config_file_from_cli = self.cli.get_config_file()

        # Check if a config file was provided via command line
        if config_file_from_cli is not None:
            self.file = config_file_from_cli
        else:
            self.logger.debug("No config file provided in command line arguments.")    

        # If no config file is set, log a message and return
        if self.file is None:
            self.logger.debug("No config file provided at all.")
            return

        # Load the configuration from the specified file
        self.load_config()

        # Update the command line defaults with values from the config file
        return self.update_defaults(cli_definitions=definitions, new_defaults=self.ini2dict(flat=True))

    def initialize_parameters(self,
                              pathToModelDir: [str, Path],
                              section: str = 'DEFAULT',
                              default_config: [str, Path] = None,
                              additional_definitions: list = None,
                              required: list = None) -> dict:
        """Initialize parameters from command line and config file.

        Args:
            pathToModelDir (str or Path): The path to the model directory.
            section (str, optional): The section name. Defaults to 'DEFAULT'.
            default_config (str or Path, optional): The default configuration file. Defaults to None.
            additional_definitions (list, optional): Additional parameter definitions. Defaults to None.
            required (list, optional): Required parameters. Defaults to None.

        Returns:
            dict: A dictionary of initialized parameters.
        """
        # Set the logger level
        self.logger.setLevel(self.log_level)
        self.logger.debug("Initializing parameters for %s", section)

        # Preserve the current class type
        current_class = self.__class__
        self.__class__ = Config

        # Set the section for reading the config file
        self.section = section

        # Check if a default config file is provided and accessible
        if default_config:
            if pathToModelDir:
                # Convert pathToModelDir to Path if it's a string
                if not isinstance(pathToModelDir, Path):
                    pathToModelDir = Path(pathToModelDir)

                # Construct the full path to the default config file
                if not default_config.startswith("/"):
                    default_config = pathToModelDir / default_config
                else:
                    self.logger.error("No path to model directory provided.")
            if not os.path.isfile(default_config):
                self.logger.error("Can't find default config file %s", default_config)
                sys.exit(404)
            else:
                self.logger.debug("Default config file found: %s", default_config)
                self.file = default_config
        else:
            self.logger.warning("No default config file provided.")

        # Update additional definitions with values from the config file
        updated_definitions = None

        if additional_definitions:
            self.logger.debug("Updating additional definitions with values from config file.")
        else:
            self.logger.debug("No additional definitions provided.")
            sys.exit(0)
            updated_definitions = additional_definitions

        # Set command line options
        self.set_command_line_options(options=additional_definitions)

        # Get command line options
        self.params = self.get_command_line_options()

        # Set input and output directories from CLI arguments
        self.input_dir = self.cli.args.input_dir
        self.output_dir = self.cli.args.output_dir
        self.log_level = self.cli.args.log_level
        self.logger.setLevel(self.log_level)
        self.logger.debug("Current log level is %s", self.log_level)

        # Update log level if set by command line
        if "log_level" in self.cli.params:
            self.logger.info("Log level set by command line, updating to %s",
                             self.cli.params["log_level"])
            self.log_level = self.params["log_level"]
            self.logger.setLevel(self.log_level)

        # Log final parameters
        self.logger.debug("Final parameters: %s", self.cli.cli_params)
        self.logger.debug("Final parameters: %s", self.params)
        self.logger.debug("Final parameters set.")

        # Set environment variables for data and output directories
        os.environ["IMPROVE_DATA_DIR"] = self.input_dir
        os.environ["IMPROVE_OUTPUT_DIR"] = self.output_dir
        os.environ["IMPROVE_LOG_LEVEL"] = self.log_level

        # Create output directory if it doesn't exist
        if not os.path.isdir(self.output_dir):
            self.logger.debug("Creating output directory: %s", self.output_dir)
            os.makedirs(self.output_dir, exist_ok=True)

        # Save final parameters to a file if specified
        final_config_file = None
        if "param_log_file" in self.params:
            self.logger.debug("Saving final parameters to file.")
            final_config_file = self.params["param_log_file"]
            self.save_parameter_file(final_config_file)

        # Restore the original class type
        self.__class__ = current_class
        return self.params


if __name__ == "__main__":
    # This block is for testing/debugging purposes
    cfg = Config()

    common_parameters = [
        {
            "name": "list_of_int",
            "dest": "loint",
            "help": "Need help to display default value",
            "nargs": "+",
            "type": int,
            "default": [100],
            "section": "DEFAULT"
        },
        {
            "name": "list_of_strings",
            "dest": "lostr",
            "nargs": "+",
            "type": str,
            "default": ['100'],
            "section": "DEFAULT"
        },
        {
            "name": "list_of_lists",
            "nargs": "+",
            "metavar": "lol",
            "dest": "l",
            "action": "append",
            "type": str,
            "default": [[1, 2, 3], [4, 5, 6]],
            "section": "DEFAULT"
        },
    ]

    current_dir = Path(__file__).resolve().parent
    test_dir = current_dir.parents[1] / "tests"

    params = cfg.load_cli_parameters(
        test_dir / "data/additional_command_line_parameters.yml")
    print(params)

    import argparse
    cfg_parser = argparse.ArgumentParser(
        description='Get the config file from command line.',
        add_help=False, )
    cfg_parser.add_argument('--config_file', metavar='INI_FILE', type=str, dest="config_file")
    sys.argv.append("--config_file")
    sys.argv.append(str(test_dir / "data/default.cfg"))

    cfg.cli.parser.add_argument('--test', metavar='TEST_COMMAND_LINE_OPTION', dest="test",
                                nargs='+',
                                type=int,
                                default=[1], help="Test command line option.")

    print(
        cfg.initialize_parameters(
            "./", additional_definitions=common_parameters + params)
    )
    print(cfg.config.items('DEFAULT', raw=False))
    print(cfg.cli.args)
    print(cfg.params)
