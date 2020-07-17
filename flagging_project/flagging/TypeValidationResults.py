class TypeValidationResults:
    def __init__(self, validation_errors=None, other_errors=None, warnings=None):
        self.validation_errors = validation_errors if validation_errors else []
        self.other_errors = other_errors if other_errors else []
        self.warnings = warnings if warnings else []

    def add_validation_error(self, error):
        self.validation_errors.apped(error)

    def add_other_error(self, error):
        self.other_errors.append(error)

    def add_warning(self, warning):
        self.warnings.append(warning)


