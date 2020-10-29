

class TransferFlaggingValidationResults:
    def __init(self, errors=None, mypy_errors=None, warnings=None, mypy_warnings=None):
        self.errors = errors if errors else []
        self.mypy_errors = mypy_errors if mypy_errors else []
        self.warnings = warnings if warnings else []
        self.mypy_warnings = mypy_warnings if mypy_warnings else[]


def _convert_FLR_to_TFLR(FLR):
    TFLR = TransferFlaggingValidationResults()

    def iterate_flagging_validation_results(FLR, TFLR, key):
        """
        
        :param FLR: FlaggingValidationResults object
        :param TFLR: TransferValidationResults object
        :param key: current parameter
        will contain results after calling front_end.FlaggingValidateLogic.validate_logic()
        :return: flagging validation results in tranfer object form
        """
        return None