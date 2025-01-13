from .._dependency import *
from ..utility import create_uuid


@dataclass
class EngineIOData:
    frame_id: int
    frame: np.ndarray
    uuid: str = field(default_factory=lambda: create_uuid())
