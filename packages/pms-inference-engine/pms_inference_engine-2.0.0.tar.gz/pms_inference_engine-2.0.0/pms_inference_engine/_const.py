from ._dependency import *

# logger
LOGGER = loguru.logger

# processor prefix
RAY_PROCESSOR_PREFIX = "Ray_"

# type def
InputTypeT = TypeVar("InputTypeT")
OutputTypeT = TypeVar("OutputTypeT")
ProcessorTypeT = TypeVar("ProcessorTypeT")
