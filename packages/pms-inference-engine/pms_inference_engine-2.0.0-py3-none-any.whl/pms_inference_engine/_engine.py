from ._dependency import *
from ._const import *
from .data_struct import EngineIOData
from ._processor_pool import ProcessorPool
from ._processor_factory import StaticProcessorFactory


class Engine:
    def __init__(
        self,
        processor_type: str,
        processor_kwargs: Dict[str, Any],
        number_of_processors: int,
        pool_search_delay: float = 0.1,
    ) -> None:
        LOGGER.info("Engine init start")
        # get_event_loop 사용 시, 기존 event loop을 가져오지만 이미 사용하고 있으므로 오류가 발생한다.
        self.event_loop = asyncio.new_event_loop()
        processors = StaticProcessorFactory.create_processors(
            number_of_processors=number_of_processors,
            processor_type=processor_type,
            processor_kwargs=processor_kwargs,
        )
        self.__pool = ProcessorPool(
            processors,
            search_delay=pool_search_delay,
        )
        self.__processor_key = processor_type
        self.__processor_kwargs = processor_kwargs
        self.__number_of_processors = number_of_processors
        LOGGER.info("Engine init end")

    def run(
        self,
        dequeue: queue.Queue,
        enqueue: queue.Queue,
    ):
        LOGGER.info("Engine run start")
        for p in self.__pool._processors:
            LOGGER.info(
                f"Engine processor[{p.id}] | live: {p.live} | ready: {p.ready} | concurrency: {p.concurrency}"
            )
            assert p.live
            assert p.ready

        async def _processing(
            loop_id: int,
            proc_pool: ProcessorPool,
            dequeue: queue.Queue,
            enqueue: queue.Queue,
        ):
            while True:
                data: EngineIOData = dequeue.get()
                if data is None:
                    LOGGER.debug(">>> Data is None")
                    dequeue.put(None)  # propagation
                    break  # end of loop
                LOGGER.debug(f"Push {data.frame_id} to the pool")
                result = await proc_pool(data=data)
                LOGGER.debug(f"Get {result.frame_id} from the pool")

                enqueue.put(result)
                LOGGER.debug(f"Enqueue result[{data.frame_id}]")
            enqueue.put(None)  # end of sequence
            LOGGER.info(f"The Engine's Processing Loop[{loop_id}] has been finished.")

        self.event_loop.run_until_complete(
            asyncio.gather(
                *[
                    self.event_loop.create_task(
                        _processing(
                            loop_id=idx,
                            proc_pool=self.__pool,
                            dequeue=dequeue,
                            enqueue=enqueue,
                        )
                    )
                    for idx in range(self.n_worker)
                ]
            )
        )
        LOGGER.info("Engine run end")

    @property
    def n_worker(self):
        return len(self.__pool)

    @property
    def n_processor(self):
        return self.__number_of_processors

    @property
    def processor_key(self):
        return self.__processor_key

    @property
    def processor_kwargs(self):
        return self.__processor_kwargs
