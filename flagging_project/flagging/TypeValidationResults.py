class TypeValidationResults:
    def __init__(self, validation_errors=None, other_errors=None, warnings=None):
        self.validation_errors = validation_errors if validation_errors else dict()
        self.other_errors = other_errors if other_errors else dict()
        self.warnings = warnings if warnings else dict()

    def add_validation_error(self, error_code, cl):
        if error_code in self.validation_errors.keys()():
            self.validation_errors[error_code].add(cl)
        else:
            self.validation_errors.setdefault(error_code, set())
            self.validation_errors[error_code].add(cl)

    def add_other_error(self, error_code, cl):
        if error_code in self.other_errors.keys():
            self.other_errors[error_code].add(cl)
        else:
            self.other_errors.setdefault(error_code, set())
            self.other_errors[error_code].add(cl)

    def add_warning(self, warning_code, cl):
        if warning_code in self.warnings.keys():
            self.warnings[warning_code].add(cl)
        else:
            self.warnings.setdefault(warning_code, set())
            self.warnings[warning_code].add(cl)


