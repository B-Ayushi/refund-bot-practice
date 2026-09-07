class ProviderUnavailableError(RuntimeError):
    """Raised when a required external travel provider is not configured."""

    def __init__(self, provider: str) -> None:
        super().__init__(f"REQUIRES_PROVIDER: {provider} provider is not configured")
        self.provider = provider