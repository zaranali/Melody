class MelodyError(Exception):
    """Base exception for all Melody errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class AssistantErr(MelodyError):
    """Exception raised for assistant-related issues."""
    pass

class PlatformError(MelodyError):
    """Exception raised for platform-specific (YouTube, Spotify, etc.) errors."""
    pass

class CallError(MelodyError):
    """Exception raised for voice chat and streaming issues."""
    pass

class UserError(MelodyError):
    """Exception raised for errors caused by user input or permissions."""
    pass
