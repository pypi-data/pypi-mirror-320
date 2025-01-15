import yaml
import logging


class ReasonerConfig:
    def __init__(self, file_path):
        self.bing_subscription_key = ""
        self.bing_endpoint = ""
        self.use_jina = False
        self.jina_api_key = ""

        self.load_config(file_path)

    def load_config(self, file_path):
        try:
            with open(file_path, 'r') as file:
                config = yaml.safe_load(file)
                reasoner_config = config.get("vital_llm_reasoner", {})
                self.bing_subscription_key = reasoner_config.get("bing_subscription_key", "")
                self.bing_endpoint = reasoner_config.get("bing_endpoint", "")
                self.use_jina = reasoner_config.get("use_jina", False)
                self.jina_api_key = reasoner_config.get("jina_api_key", "")
                logging.info("Configuration loaded successfully.")
        except FileNotFoundError:
            logging.info(f"Configuration file not found at: {file_path}")
        except yaml.YAMLError as e:
            logging.info(f"Error parsing YAML file: {e}")
