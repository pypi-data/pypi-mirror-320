import os
import logging

import json as js
import traceback as tb

from datetime import datetime as dt, timezone as tz
from typing import Dict, Optional

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

from dotenv import find_dotenv, load_dotenv

_env = find_dotenv(".env")

if _env:
    load_dotenv(_env)

log = logging.getLogger(__name__)


class KeyVaultInterface:
    """
    This class serves as an interface for interacting with Azure Key Vault.

    Implements a singleton pattern to ensure only one instance is created.
    It handles the interaction with Azure Key Vault to retrieve secrets and manage them in memory.

    :param key_vault_name: The Azure Key Vault name.
    :param tenant_id: Azure AD Tenant ID.
    :param client_id: Azure Client ID.
    :param secrets_to_load: Optional dictionary of secrets to load into the interface.
    :type secrets_to_load: dict, optional
    """

    # _instance = None  # Singleton instance reference

    # def __new__(cls, *args, **kwargs):
    #     """
    #     Singleton pattern: Ensures only one instance of the class is created.

    #     :return: The single instance of the KeyVaultInterface class.
    #     :rtype: KeyVaultInterface
    #     """
    #     if not cls._instance:
    #         cls._instance = super(KeyVaultInterface, cls).__new__(cls)
    #     return cls._instance

    def __init__(
        self,
        key_vault_name: str,
        tenant_id: str,
        client_id: str,
        client_secret_var_name: str = "KEY_VAULT_SECRET",
        secrets_to_load: Optional[Dict[str, str]] = None,
    ):
        """
        Initializes the Key Vault Interface and loads secrets.

        Args:
            key_vault_name (str): The Azure Key Vault name.
            tenant_id (str): Azure AD Tenant ID.
            client_id (str): Azure Client ID.
            client_secret_var_name (str): The environment variable to use to load the client secret matching the client ID.
            secrets_to_load (dict, optional): Secrets to load into the interface.
        """
        # if hasattr(self, "initialized"):  # Prevent reinitialization
        #     return

        self.key_vault_name = key_vault_name
        self.secrets_to_load = secrets_to_load or {}
        self.loaded_secrets = {}

        # Fetch the client_secret from the environment
        client_secret = os.getenv(client_secret_var_name)
        if not client_secret:
            raise ValueError(
                f"{client_secret_var_name} environment variable is required but not set."
            )

        if False:
            """
            Disabled since it could lead to conflict in cases where more instances are created
            and the same env var is needed, this wasn't the starting usage idea, but it's better
            to handle all the scenarios until the flow is standardized
            """
            self._clear_env_from_var(client_secret_var_name)

        # Initialize Azure Key Vault client
        self.credentials = ClientSecretCredential(
            tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
        )
        self.kv_address = f"https://{key_vault_name}.vault.azure.net/"
        self.key_vault_client = SecretClient(
            vault_url=self.kv_address, credential=self.credentials
        )

        # Load initial secrets
        self.load_secrets()
        log.info("Key Vault Interface initialized")

        self.initialized = True  # Mark as initialized

    @classmethod
    def from_json(self, conf, _raise=False):
        if not isinstance(conf, dict):
            msg = f"tried to instance key vault interface from json; expectd config as dict, got {type(conf)}"
            if _raise:
                raise Exception(msg)
            log.error(msg)
            return None

        try:
            return KeyVaultInterface(
                key_vault_name=conf.get("key_vault_name"),
                tenant_id=conf.get("tenant_id"),
                client_id=conf.get("client_id"),
                client_secret_var_name=conf.get("client_secret_var_name"),
                secrets_to_load=conf.get("secrets_to_load"),
            )
        except Exception as e:
            if _raise:
                log.error(
                    f"failed to initialize key vault interface from json:\n{tb.format_exc()}"
                )
                raise e

            return None

    @staticmethod
    def apply_prefix_to_strings(
        prefix: str, string_map: dict
    ):

        if not isinstance(prefix, str):
            prefix = ""

        if isinstance(string_map, dict):
            secrets = {
                alias: f"{prefix}{key_name}"
                for alias, key_name in string_map.items()
                if isinstance(key_name, str)
            }
        else:
            secrets = {}

        return secrets

    def get(self, secret_name: str) -> str:
        """
        Retrieve a secret value from loaded secrets.

        Args:
            secret_name (str): Name of the secret.

        Returns:
            str: Value of the secret or None if not found.

        :raises ValueError: If the secret_name is not a string.
        """
        if not isinstance(secret_name, str):
            raise ValueError(f"Expected str for secret name, got {type(secret_name)}")

        if secret_name not in self.loaded_secrets:
            log.warning(f"{secret_name} not present in loaded secrets. Returning None.")
        return self.loaded_secrets.get(secret_name)

    def _clear_env_from_var(self, client_secret_var_name):
        # Remove the client_secret from the environment for security
        try:
            os.environ.pop(client_secret_var_name)
            log.info(f"Removed {client_secret_var_name} from runtime environment")
        except Exception as e:
            log.warning(f"Failed to clean {client_secret_var_name}: {e}")

    def __get_secret_from_kv(self, secret_name: str) -> Optional[str]:
        """
        Retrieves a secret value from Azure Key Vault.

        Args:
            secret_name (str): Name of the secret in Key Vault.

        Returns:
            str or None: Secret value, or None if expired or unavailable.

        :raises Exception: If unable to retrieve the secret from Azure Key Vault.
        """
        try:
            secret = self.key_vault_client.get_secret(secret_name)

            if secret.properties.expires_on and secret.properties.expires_on <= dt.now(
                tz=tz.utc
            ):
                log.error(
                    f"Secret {secret_name} is expired as of {secret.properties.expires_on}"
                )
                return None

            if secret.properties.not_before and secret.properties.not_before >= dt.now(
                tz=tz.utc
            ):
                log.error(
                    f"Secret {secret_name} is not valid until {secret.properties.not_before}"
                )
                return None

            secret_value = secret.value

            if secret.properties.content_type == "json":
                try:
                    secret_value = js.loads(secret_value)
                except Exception:
                    log.error(
                        f"Failed to parse secret {secret_name} as JSON:\n{tb.format_exc()}"
                    )

            return secret_value

        except Exception as e:
            log.error(f"Failed to retrieve secret {secret_name} from Key Vault: {e}")
            return None

    def load_secrets(self) -> None:
        """
        Loads all secrets specified in 'secrets_to_load' into memory.

        Iterates over the secrets_to_load dictionary and fetches each secret from the Azure Key Vault.
        """
        for alias, secret_name in self.secrets_to_load.items():
            self._load_secret(alias, secret_name)

    def _load_secret(self, alias: str, secret_name: str) -> None:
        """
        Loads a single secret into memory.

        Args:
            alias (str): Alias for the secret.
            secret_name (str): Actual name of the secret in Key Vault.

        :raises Exception: If loading the secret fails.
        """
        try:
            secret = self.__get_secret_from_kv(secret_name)
            self.loaded_secrets[alias] = secret
            log.info(f"Secret '{secret_name}' loaded under alias '{alias}'.")
        except Exception as e:
            log.error(f"Failed to load secret '{secret_name}': {e}")

    def forget_secret(self, alias: str) -> None:
        """
        Removes a secret from memory.

        Args:
            alias (str): Alias of the secret to remove.

        :raises KeyError: If the secret alias is not found in the loaded secrets.
        """
        if alias in self.loaded_secrets:
            self.loaded_secrets.pop(alias)
            log.info(f"Secret '{alias}' removed from memory.")
        else:
            log.warning(f"Secret '{alias}' is not loaded.")

    def update_and_reload_secrets(self, new_secrets: Dict[str, str]) -> None:
        """
        Updates the list of secrets to load and reloads them.

        Args:
            new_secrets (dict): Dictionary of new secrets to load.

        :raises TypeError: If new_secrets is not a dictionary.
        """
        if not isinstance(new_secrets, dict):
            log.error(f"Expected dict, got {type(new_secrets)}")
            return

        self.secrets_to_load.update(new_secrets)
        self.load_secrets()
