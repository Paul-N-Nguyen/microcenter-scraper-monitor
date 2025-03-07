import yaml

def load_config(config_path="config.yaml") -> dict:
    """
    Loads YAML configuration file
    """
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

# Load configuration
config = load_config()
