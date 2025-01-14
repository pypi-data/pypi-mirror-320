class LogAnalyzerError(Exception):
    pass

class UnsupportedFileFormatError(LogAnalyzerError):
    def __init__(self, message="Unsupported file format"):
        self.message = message
        super().__init__(self.message)
