class TypeValidationResults:
    def __init__(self, validation_errors=None, other_errors=None, warnings=None):
        self.validation_errors = validation_errors if validation_errors else dict()
        self.other_errors = other_errors if other_errors else dict()
        self.warnings = warnings if warnings else dict()

    def add_validation_error(self, error_code, codelocation):
        self.validation_errors[error_code] = codelocation

    def add_other_error(self, error_code, codelocation):
        self.other_errors[error_code] = codelocation

    def add_warning(self, warning, codelocation):
        self.warnings[warning] = codelocation