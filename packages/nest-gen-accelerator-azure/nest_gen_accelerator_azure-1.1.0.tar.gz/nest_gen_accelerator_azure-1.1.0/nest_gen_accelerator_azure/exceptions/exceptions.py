class InvalidLLMResponseException(Exception):
    """Base exception for all invalid LLM response cases."""

    def __init__(self, message="The LLM response was invalid", details=None):
        super().__init__(message)
        self.details = details or {}


class ContentPolicyViolationException(Exception):
    """Exception raised when content violates the content management policy."""

    def __init__(
        self,
        message: str ="The response was filtered for not respecting the content management policy",
        details: dict = None,
    ):
        super().__init__(message)
        self.details = details or {}
