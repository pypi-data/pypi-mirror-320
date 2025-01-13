# pms-inference-engine

pms에서 사용하기 위한 inference engine입니다.

## Install

```bash
pip install pms-inference-engine
```

## Use

```python
import pms_inference_engine as E

# processor type in engine
processor_type = "SleepAndPassProcessor"

# number of processor in engine
nprocessors = 4

# params for construct processor
processor_kwargs = {
    "concurrency": 2,
    "sleep_time": 0.1,
} 

# create engine
engine = E.Engine(
    processor_type=processor_type,
    number_of_processors=nprocessors,
    processor_kwargs=processor_kwargs,
)

# create queue for engine
dequeue = Queue()
enqueue = Queue()

# input data
for i in range(nframe):
    dequeue.put(E.EngineIOData(i, np.zeros((10, 10))))

# add exit flag
# - if you don't add the exit flag, the engine will run forever
dequeue.put(None)

# run engine
engine.run(dequeue=dequeue, enqueue=enqueue)
```
