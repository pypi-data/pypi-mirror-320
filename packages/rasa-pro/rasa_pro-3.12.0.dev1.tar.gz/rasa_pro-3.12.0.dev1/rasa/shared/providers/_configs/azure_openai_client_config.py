from __future__ import annotations

import logging
from abc import abstractmethod
from dataclasses import asdict, dataclass, field
from enum import Enum
from functools import lru_cache
from typing import Any, Callable, Coroutine, Dict, List, Optional, Protocol, Set

import structlog
from azure.core.credentials import TokenProvider
from azure.identity import (
    CertificateCredential,
    ClientSecretCredential,
    DefaultAzureCredential,
    get_bearer_token_provider,
)

from rasa.shared.constants import (
    API_BASE_CONFIG_KEY,
    API_KEY,
    API_TYPE_CONFIG_KEY,
    API_VERSION_CONFIG_KEY,
    AZURE_API_TYPE,
    AZURE_OPENAI_PROVIDER,
    DEPLOYMENT_CONFIG_KEY,
    DEPLOYMENT_NAME_CONFIG_KEY,
    ENGINE_CONFIG_KEY,
    LANGCHAIN_TYPE_CONFIG_KEY,
    MODEL_CONFIG_KEY,
    MODEL_NAME_CONFIG_KEY,
    N_REPHRASES_CONFIG_KEY,
    OPENAI_API_BASE_CONFIG_KEY,
    OPENAI_API_TYPE_CONFIG_KEY,
    OPENAI_API_VERSION_CONFIG_KEY,
    PROVIDER_CONFIG_KEY,
    RASA_TYPE_CONFIG_KEY,
    REQUEST_TIMEOUT_CONFIG_KEY,
    STREAM_CONFIG_KEY,
    TIMEOUT_CONFIG_KEY,
)
from rasa.shared.providers._configs.utils import (
    raise_deprecation_warnings,
    resolve_aliases,
    validate_forbidden_keys,
    validate_required_keys,
)

structlogger = structlog.get_logger()

DEPRECATED_ALIASES_TO_STANDARD_KEY_MAPPING = {
    # Deployment name aliases
    DEPLOYMENT_NAME_CONFIG_KEY: DEPLOYMENT_CONFIG_KEY,
    ENGINE_CONFIG_KEY: DEPLOYMENT_CONFIG_KEY,
    # Provider aliases
    RASA_TYPE_CONFIG_KEY: PROVIDER_CONFIG_KEY,
    LANGCHAIN_TYPE_CONFIG_KEY: PROVIDER_CONFIG_KEY,
    # API type aliases
    OPENAI_API_TYPE_CONFIG_KEY: API_TYPE_CONFIG_KEY,
    # API base aliases
    OPENAI_API_BASE_CONFIG_KEY: API_BASE_CONFIG_KEY,
    # API version aliases
    OPENAI_API_VERSION_CONFIG_KEY: API_VERSION_CONFIG_KEY,
    # Model name aliases
    MODEL_NAME_CONFIG_KEY: MODEL_CONFIG_KEY,
    # Timeout aliases
    REQUEST_TIMEOUT_CONFIG_KEY: TIMEOUT_CONFIG_KEY,
}

REQUIRED_KEYS = [DEPLOYMENT_CONFIG_KEY]

FORBIDDEN_KEYS = [
    STREAM_CONFIG_KEY,
    N_REPHRASES_CONFIG_KEY,
]


AZURE_CLIENT_ID_FIELD = "client_id"
AZURE_CLIENT_SECRET_FIELD = "client_secret"
AZURE_TENANT_ID_FIELD = "tenant_id"
AZURE_CERTIFICATE_PATH_FIELD = "certificate_path"
AZURE_CERTIFICATE_PASSWORD_FIELD = "certificate_password"
AZURE_SEND_CERTIFICATE_CHAIN_FIELD = "send_certificate_chain"
AZURE_SCOPES_FIELD = "scopes"
AZURE_AUTHORITY_FIELD = "authority_host"
AZURE_DISABLE_INSTANCE_DISCOVERY_FIELD = "disable_instance_discovery"
OAUTH_TYPE_FIELD = "type"
AZURE_OAUTH_KEY = "oauth"


azure_logger = logging.getLogger("azure")
azure_logger.setLevel(logging.DEBUG)


class AzureOAuthType(str, Enum):
    AZURE_DEFAULT = "default"
    AZURE_CLIENT_SECRET = "client_secret"
    AZURE_CLIENT_CERTIFICATE = "client_certificate"
    # Invalid type is used to indicate that the type
    # configuration is invalid or not set.
    INVALID = "invalid"

    @staticmethod
    def from_string(value: Optional[str]) -> AzureOAuthType:
        if value is None or value not in AzureOAuthType.valid_string_values():
            return AzureOAuthType.INVALID

        return AzureOAuthType(value)

    @staticmethod
    def valid_string_values() -> Set[str]:
        return {e.value for e in AzureOAuthType.valid_values()}

    @staticmethod
    def valid_values() -> Set[AzureOAuthType]:
        return {
            AzureOAuthType.AZURE_DEFAULT,
            AzureOAuthType.AZURE_CLIENT_SECRET,
            AzureOAuthType.AZURE_CLIENT_CERTIFICATE,
        }


class AzureAuthType(str, Enum):
    API_KEY = "api_key"
    OAUTH = "oauth"

    @staticmethod
    def from_string(value: str) -> AzureAuthType:
        try:
            return AzureAuthType(value)
        except ValueError:
            raise ValueError(f"Invalid AzureAuthType value: {value}")

    def __str__(self) -> str:
        return self.value


DEFAULT_AUTH_TYPE = AzureAuthType.API_KEY


BearerTokenProvider = Callable[[], Coroutine[Any, Any, str]]


class AzureEntraIDCredential(Protocol):
    @abstractmethod
    def create_azure_credential(self) -> TokenProvider: ...
    @abstractmethod
    def to_dict(self) -> dict: ...


@dataclass
class AzureClientCredentialsConfig:
    """Azure OAuth client credentials configuration.

    Attributes:
        client_id: The client ID.
        client_secret: The client secret.
        tenant_id: The tenant ID.
        authority_host: The authority host.
        disable_instance_discovery: Whether to disable instance discovery. This is used
            to disable fetching metadata from the Azure Instance Metadata Service.
    """

    client_id: str
    client_secret: str
    tenant_id: str
    authority_host: Optional[str] = None
    disable_instance_discovery: bool = False

    @staticmethod
    def required_fields() -> Set[str]:
        """Returns the required fields for the configuration."""
        return {AZURE_CLIENT_ID_FIELD, AZURE_TENANT_ID_FIELD, AZURE_CLIENT_SECRET_FIELD}

    @staticmethod
    def config_has_required_fields(config: Dict[str, Any]) -> bool:
        """Check if the configuration has all the required fields."""
        return AzureClientCredentialsConfig.required_fields().issubset(
            set(config.keys())
        )

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> AzureClientCredentialsConfig:
        """Initializes a dataclass from the passed config.

        Args:
            config: (dict) The config from which to initialize.

        Returns:
            AzureClientCredentialsConfig
        """
        if not cls.config_has_required_fields(config):
            message = (
                f"A configuration for Azure client credentials "
                f"must contain the following keys: {cls.required_fields()}"
            )
            structlogger.error(
                "azure_client_credentials_config.missing_required_keys",
                message=message,
                config=config,
            )
            raise ValueError(message)

        return cls(
            client_id=config.pop(AZURE_CLIENT_ID_FIELD),
            client_secret=config.pop(AZURE_CLIENT_SECRET_FIELD),
            tenant_id=config.pop(AZURE_TENANT_ID_FIELD),
            authority_host=config.pop(AZURE_AUTHORITY_FIELD, None),
            disable_instance_discovery=config.pop(
                AZURE_DISABLE_INSTANCE_DISCOVERY_FIELD, False
            ),
        )

    def to_dict(self) -> dict:
        """Converts the config instance into a dictionary."""
        result = asdict(self)
        result[OAUTH_TYPE_FIELD] = AzureOAuthType.AZURE_CLIENT_SECRET.value
        return result

    def create_azure_credential(self) -> TokenProvider:
        return create_client_credentials(
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
            authority_host=self.authority_host,
            disable_instance_discovery=self.disable_instance_discovery,
        )


@lru_cache
def create_client_credentials(
    client_id: str,
    client_secret: str,
    tenant_id: str,
    authority_host: Optional[str] = None,
    disable_instance_discovery: bool = False,
) -> ClientSecretCredential:
    """Create a ClientSecretCredential.

    We cache the result of this function to avoid creating multiple instances
    of the same credential. This makes it possible to utilise the token caching
    functionality of the azure-identity library.

    Args:
        client_id: The client ID.
        client_secret: The client secret.
        tenant_id: The tenant ID.
        authority_host: The authority host.
        disable_instance_discovery: Whether to disable instance discovery. This is used
            to disable fetching metadata from the Azure Instance Metadata Service.

    Returns:
        ClientSecretCredential
    """
    return ClientSecretCredential(
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id,
        authority=authority_host,
        disable_instance_discovery=disable_instance_discovery,
    )


@dataclass
class AzureClientCertificateConfig:
    """Azure OAuth client certificate configuration.

    Attributes:
        client_id: The client ID.
        tenant_id: The tenant ID.
        certificate_path: The path to the certificate file.
        certificate_password: The certificate password.
        send_certificate_chain: Whether to send the certificate chain.
        authority_host: The authority host.
        disable_instance_discovery: Whether to disable instance discovery. This is used
            to disable fetching metadata from the Azure Instance Metadata Service.
    """

    client_id: str
    tenant_id: str
    certificate_path: str
    certificate_password: Optional[str] = None
    send_certificate_chain: bool = False
    authority_host: Optional[str] = None
    disable_instance_discovery: bool = False

    @staticmethod
    def required_fields() -> Set[str]:
        """Returns the required fields for the configuration."""
        return {
            AZURE_CLIENT_ID_FIELD,
            AZURE_TENANT_ID_FIELD,
            AZURE_CERTIFICATE_PATH_FIELD,
            AZURE_CERTIFICATE_PASSWORD_FIELD,
        }

    @staticmethod
    def config_has_required_fields(config: Dict[str, Any]) -> bool:
        """Check if the configuration has all the required fields."""
        return AzureClientCertificateConfig.required_fields().issubset(
            set(config.keys())
        )

    @classmethod
    def from_config(
        cls, config: Dict[str, Any]
    ) -> Optional[AzureClientCertificateConfig]:
        """Initializes a dataclass from the passed config.

        Args:
            config: (dict) The config from which to initialize.

        Returns:
            AzureClientCertificateConfig
        """
        if not cls.config_has_required_fields(config):
            message = (
                f"A configuration for Azure client certificate "
                f"must contain "
                f"the following keys: {cls.required_fields()}"
            )
            structlogger.error(
                "azure_client_certificate_config.validation_error",
                message=message,
                config=config,
            )
            raise ValueError(message)

        return cls(
            client_id=config[AZURE_CLIENT_ID_FIELD],
            tenant_id=config[AZURE_TENANT_ID_FIELD],
            certificate_path=config[AZURE_CERTIFICATE_PATH_FIELD],
            certificate_password=config.get(AZURE_CERTIFICATE_PASSWORD_FIELD, None),
            authority_host=config.get(AZURE_AUTHORITY_FIELD, None),
            send_certificate_chain=config.get(
                AZURE_SEND_CERTIFICATE_CHAIN_FIELD, False
            ),
            disable_instance_discovery=config.get(
                AZURE_DISABLE_INSTANCE_DISCOVERY_FIELD, False
            ),
        )

    def to_dict(self) -> dict:
        """Converts the config instance into a dictionary."""
        result = asdict(self)
        result[OAUTH_TYPE_FIELD] = AzureOAuthType.AZURE_CLIENT_CERTIFICATE.value
        return result

    def create_azure_credential(self) -> TokenProvider:
        return create_certificate_credentials(
            client_id=self.client_id,
            tenant_id=self.tenant_id,
            certificate_path=self.certificate_path,
            password=self.certificate_password,
            send_certificate_chain=self.send_certificate_chain,
            authority_host=self.authority_host,
            disable_instance_discovery=self.disable_instance_discovery,
        )


@lru_cache
def create_certificate_credentials(
    tenant_id: str,
    client_id: str,
    certificate_path: Optional[str] = None,
    password: Optional[str] = None,
    send_certificate_chain: bool = False,
    authority_host: Optional[str] = None,
    disable_instance_discovery: bool = False,
) -> CertificateCredential:
    """Create a CertificateCredential.

    We cache the result of this function to avoid creating multiple instances
    of the same credential. This makes it possible to utilise the token caching
    functionality of the azure-identity library.

    Args:
        tenant_id: The tenant ID.
        client_id: The client ID.
        certificate_path: The path to the certificate file.
        password: The certificate password.
        send_certificate_chain: Whether to send the certificate chain.
        authority_host: The authority host.
        disable_instance_discovery: Whether to disable instance discovery. This is used

    Returns:
        CertificateCredential
    """

    return CertificateCredential(
        client_id=client_id,
        tenant_id=tenant_id,
        certificate_path=certificate_path,
        password=password.encode("utf-8") if password else None,
        send_certificate_chain=send_certificate_chain,
        authority=authority_host,
        disable_instance_discovery=disable_instance_discovery,
    )


@dataclass
class AzureOAuthDefaultCredentialsConfig:
    """Azure OAuth default credentials configuration.

    Attributes:
        authority_host: The authority host.
    """

    authority_host: Optional[str] = None

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> AzureOAuthDefaultCredentialsConfig:
        """Initializes a dataclass from the passed config.

        Args:
            config: (dict) The config from which to initialize.

        Returns:
            AzureOAuthDefaultCredentialsConfig
        """
        return cls(authority_host=config.pop(AZURE_AUTHORITY_FIELD, None))

    def to_dict(self) -> dict:
        """Converts the config instance into a dictionary."""
        result = asdict(self)
        result[OAUTH_TYPE_FIELD] = AzureOAuthType.AZURE_DEFAULT.value
        return result

    def create_azure_credential(self) -> TokenProvider:
        return create_default_credentials(authority_host=self.authority_host)


@lru_cache
def create_default_credentials(
    authority_host: Optional[str] = None,
) -> DefaultAzureCredential:
    """Create a DefaultAzureCredential.

    We cache the result of this function to avoid creating multiple instances
    of the same credential. This makes it possible to utilise the token caching
    functionality of the azure-identity library.

    Args:
        authority_host: The authority host.

    Returns:
        DefaultAzureCredential
    """
    return DefaultAzureCredential(authority=authority_host)


@dataclass
class AzureOAuthConfig:
    scopes: List[str]
    azure_credentials: Optional[AzureEntraIDCredential] = None

    @classmethod
    def from_config(cls, oauth_config: Dict[str, Any]) -> AzureOAuthConfig:
        """Initializes a dataclass from the passed config.

        Args:
            oauth_config: (dict) The config from which to initialize.

        Returns:
            AzureOAuthConfig
        """
        oauth_type = AzureOAuthType.from_string(
            oauth_config.pop(OAUTH_TYPE_FIELD, None)
        )

        if oauth_type == AzureOAuthType.INVALID:
            message = (
                "Azure Entra ID oauth configuration must contain "
                f"'{OAUTH_TYPE_FIELD}' field and it must be set to one of the "
                f"following values: {AzureOAuthType.valid_string_values()}, "
            )
            structlogger.error(
                "azure_oauth_config.missing_oauth_type",
                message=message,
            )
            raise ValueError(message)

        azure_credentials = None
        if oauth_type == AzureOAuthType.AZURE_CLIENT_SECRET:
            azure_credentials = AzureClientCredentialsConfig.from_config(oauth_config)
        elif oauth_type == AzureOAuthType.AZURE_CLIENT_CERTIFICATE:
            azure_credentials = AzureClientCertificateConfig.from_config(oauth_config)
        elif oauth_type == AzureOAuthType.AZURE_DEFAULT:
            azure_credentials = AzureOAuthDefaultCredentialsConfig.from_config(
                oauth_config
            )

        scopes = oauth_config.pop(AZURE_SCOPES_FIELD, "")

        if not scopes:
            message = "Azure Entra ID scopes cannot be empty."
            structlogger.error(
                "azure_oauth_config.scopes_empty",
                message=message,
            )
            raise ValueError(message)

        if isinstance(scopes, str):
            scopes = [scopes]

        return cls(azure_credentials=azure_credentials, scopes=scopes)

    def create_azure_credential(
        self,
    ) -> TokenProvider:
        return self.azure_credentials.create_azure_credential()

    def to_dict(self) -> dict:
        """Converts the config instance into a dictionary."""
        credentials_dict = (
            self.azure_credentials.to_dict() if self.azure_credentials else {}
        )
        result = asdict(self)
        result.update(credentials_dict)
        result.pop("azure_credentials", None)
        return result

    def get_bearer_token_provider(self) -> BearerTokenProvider:
        return get_bearer_token_provider(self.create_azure_credential(), *self.scopes)

    def get_bearer_token(self) -> str:
        token = self.create_azure_credential().get_token(*self.scopes).token
        return token


@dataclass
class AzureOpenAIClientConfig:
    """Parses configuration for Azure OpenAI client, resolves aliases and
    raises deprecation warnings.

    Raises:
        ValueError: Raised in cases of invalid configuration:
            - If any of the required configuration keys are missing.
            - If `api_type` has a value different from `azure`.
    """

    deployment: str

    model: Optional[str]
    api_base: Optional[str]
    api_version: Optional[str]
    # API Type is not used by LiteLLM backend, but we define
    # it here for backward compatibility.
    api_type: Optional[str] = AZURE_API_TYPE
    # Provider is not used by LiteLLM backend, but we define it here since it's
    # used as switch between different clients.
    provider: str = AZURE_OPENAI_PROVIDER

    # OAuth related parameters
    oauth: Optional[AzureOAuthConfig] = None

    extra_parameters: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.provider != AZURE_OPENAI_PROVIDER:
            message = f"Provider must be set to '{AZURE_OPENAI_PROVIDER}'."
            structlogger.error(
                "azure_openai_client_config.validation_error",
                message=message,
                provider=self.provider,
            )
            raise ValueError(message)
        if self.deployment is None:
            message = "Deployment cannot be set to None."
            structlogger.error(
                "azure_openai_client_config.validation_error",
                message=message,
                deployment=self.deployment,
            )
            raise ValueError(message)

    @classmethod
    def from_dict(cls, config: dict) -> AzureOpenAIClientConfig:
        """Initializes a dataclass from the passed config.

        Args:
            config: (dict) The config from which to initialize.

        Raises:
            ValueError: Raised in cases of invalid configuration:
                - If any of the required configuration keys are missing.
                - If `api_type` has a value different from `azure`.

        Returns:
            AzureOpenAIClientConfig
        """
        # Check for deprecated keys
        raise_deprecation_warnings(config, DEPRECATED_ALIASES_TO_STANDARD_KEY_MAPPING)
        # Resolve any potential aliases
        config = cls.resolve_config_aliases(config)
        # Validate that required keys are set
        validate_required_keys(config, REQUIRED_KEYS)
        # Validate that the forbidden keys are not present
        validate_forbidden_keys(config, FORBIDDEN_KEYS)
        # Init client config

        has_api_key = config.get(API_KEY, None) is not None
        has_oauth_key = config.get(AZURE_OAUTH_KEY, None) is not None

        if has_api_key and has_oauth_key:
            message = (
                "Azure OpenAI client configuration cannot contain "
                "both 'api_key' and 'oauth' fields. Please provide either "
                "'api_key' or 'oauth' fields."
            )
            structlogger.error(
                "azure_openai_client_config.multiple_auth_types_specified",
                message=message,
            )
            raise ValueError(message)

        oauth = None
        if has_oauth_key:
            oauth = AzureOAuthConfig.from_config(config.pop(AZURE_OAUTH_KEY))

        this = AzureOpenAIClientConfig(
            # Required parameters
            deployment=config.pop(DEPLOYMENT_CONFIG_KEY),
            # Pop the 'provider' key. Currently, it's *optional* because of
            # backward compatibility with older versions.
            provider=config.pop(PROVIDER_CONFIG_KEY, AZURE_OPENAI_PROVIDER),
            # Optional
            api_type=config.pop(API_TYPE_CONFIG_KEY, AZURE_API_TYPE),
            model=config.pop(MODEL_CONFIG_KEY, None),
            # Optional, can also be set through environment variables
            # in clients.
            api_base=config.pop(API_BASE_CONFIG_KEY, None),
            api_version=config.pop(API_VERSION_CONFIG_KEY, None),
            # OAuth related parameters, set only if auth_type is set to 'entra_id'
            oauth=oauth,
            # The rest of parameters (e.g. model parameters) are considered
            # as extra parameters (this also includes timeout).
            extra_parameters=config,
        )
        return this

    def to_dict(self) -> dict:
        """Converts the config instance into a dictionary."""
        d = asdict(self)
        # Extra parameters should also be on the top level
        d.pop("extra_parameters", None)
        d.update(self.extra_parameters)

        d.pop("oauth", None)
        d.update({"oauth": self.oauth.to_dict()} if self.oauth else {})
        return d

    @staticmethod
    def resolve_config_aliases(config: Dict[str, Any]) -> Dict[str, Any]:
        return resolve_aliases(config, DEPRECATED_ALIASES_TO_STANDARD_KEY_MAPPING)


def is_azure_openai_config(config: dict) -> bool:
    """Check whether the configuration is meant to configure
    an Azure OpenAI client.
    """
    # Resolve any aliases that are specific to Azure OpenAI configuration
    config = AzureOpenAIClientConfig.resolve_config_aliases(config)

    # Case: Configuration contains `provider: azure`.
    if config.get(PROVIDER_CONFIG_KEY) == AZURE_OPENAI_PROVIDER:
        return True

    # Case: Configuration contains `deployment` key
    # (specific to Azure OpenAI configuration)
    if (
        config.get(DEPLOYMENT_CONFIG_KEY) is not None
        and config.get(PROVIDER_CONFIG_KEY) is None
    ):
        return True

    return False
