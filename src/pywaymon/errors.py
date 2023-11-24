class PyWayMonError(Exception):
    """Base Error for pywaymon."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TipTypeError(Exception):
    """Unrecognised tip state"""

    def __init__(self, tip_type):
        super().__init__(f'{tip_type} not recognized.')


class UnitsError(Exception):
    """Value is expressed with non-standard unit prefix."""

    def __init__(self, pref):
        super().__init__(f'Non-standard prefix {pref} not recognized.')
