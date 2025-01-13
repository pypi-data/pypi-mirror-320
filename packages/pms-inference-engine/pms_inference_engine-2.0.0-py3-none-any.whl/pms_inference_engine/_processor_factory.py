from ._dependency import *
from ._const import *
from ._ray_processor import RayProcessor
from .interface import IEngineProcessor


def register(__cls: Type[ProcessorTypeT]) -> Type[ProcessorTypeT]:
    StaticProcessorFactory._set_processor(__cls)
    return __cls


class StaticProcessorFactory:

    __PROC_LIST = []

    @classmethod
    def _set_processor(cls, __cls: Type[ProcessorTypeT]):
        assert issubclass(
            __cls, IEngineProcessor
        ), f"[{__cls}] is not subclass of {IEngineProcessor}"
        assert (
            __cls not in StaticProcessorFactory.__PROC_LIST
        ), f"[{__cls}] is already registered."
        cls.__PROC_LIST.append(__cls)

    @classmethod
    def __wrap_with_ray(cls, target_class: type, **kwargs) -> RayProcessor:
        return RayProcessor(target_class=target_class, **kwargs)

    @classmethod
    def is_wrapped_ray(cls, processor_type: str) -> bool:
        return processor_type.startswith(RAY_PROCESSOR_PREFIX)

    @classmethod
    def get_local_processor_type(cls, processor_type: str) -> str:
        assert cls.is_wrapped_ray(
            processor_type
        ), f"{processor_type} is not ray(remote) processor type"
        processor_type = processor_type.replace(RAY_PROCESSOR_PREFIX, "", 1)
        return processor_type

    @classmethod
    def is_valid_processor_type(cls, processor_type: str) -> bool:
        processor_keys = [p.__name__ for p in cls.__PROC_LIST]
        if cls.is_wrapped_ray(processor_type):
            processor_type = cls.get_local_processor_type(processor_type)
        return processor_type in processor_keys

    @classmethod
    def get_processor_types(cls) -> List[str]:
        return [p.__name__ for p in cls.__PROC_LIST]

    @classmethod
    def create_processor(
        cls,
        processor_type: str,
        processor_idx: int,
        **kwargs,
    ) -> IEngineProcessor:
        assert cls.is_valid_processor_type(
            processor_type
        ), f"'{processor_type}' is wrong processor type."
        kwargs["index"] = processor_idx
        is_ray_object = cls.is_wrapped_ray(processor_type)
        if is_ray_object == True:
            processor_type = cls.get_local_processor_type(processor_type)
        processor_keys = cls.get_processor_types()
        p_idx = processor_keys.index(processor_type)
        target_class = cls.__PROC_LIST[p_idx]
        return (
            cls.__wrap_with_ray(target_class, **kwargs)
            if is_ray_object
            else target_class(**kwargs)
        )

    @classmethod
    def create_processors(
        cls,
        number_of_processors: int,
        processor_type: str,
        processor_kwargs: Dict[str, Any],
    ) -> List[IEngineProcessor[Any, Any]]:
        assert number_of_processors > 0, "number of processors must be n > 0"
        assert StaticProcessorFactory.is_valid_processor_type(
            processor_type
        ), f"{processor_type} is wrong processor type"
        if StaticProcessorFactory.is_wrapped_ray(processor_type):
            assert (
                ray.is_initialized()
            ), "The processor is Ray(remote) type. but ray session is not initialized"
        processors = [
            StaticProcessorFactory.create_processor(
                processor_type=processor_type,
                processor_idx=idx,
                **processor_kwargs,
            )
            for idx in range(number_of_processors)
        ]
        return processors
