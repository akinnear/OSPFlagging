class FlagLogicInformation:
    def __init__(self, used_variables=None, assigned_variables=None, referenced_functions=None,
                 defined_functions=None, defined_classes=None, referenced_modules=None,
                 referenced_flags=None, return_points=None, errors=None, validation_results=None):
        self.used_variables = used_variables if used_variables else {}
        self.assigned_variables = assigned_variables if assigned_variables else {}
        self.referenced_functions = referenced_functions if referenced_functions else {}
        self.defined_functions = defined_functions if defined_functions else {}
        self.defined_classes = defined_classes if defined_classes else {}
        self.referenced_modules = referenced_modules if referenced_modules else {}
        self.referenced_flags = referenced_flags if referenced_flags else {}
        self.return_points = return_points if return_points else set()
        self.errors = errors if errors else []
        self.validation_results = validation_results if validation_results else {}