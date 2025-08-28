import time
from Stopwatch import Stopwatch


print(f"clock info 'monotonic'      {time.get_clock_info('monotonic')}")
print(f"clock info 'perf_counter'   {time.get_clock_info('perf_counter')}")
print(f"clock info 'process_time'   {time.get_clock_info('process_time')}")
print(f"clock info 'thread_time'    {time.get_clock_info('thread_time')}")
print(f"clock info 'time'           {time.get_clock_info('time')}")

for i in range(10):
    t0 = time.time()
    t1 = time.time()
    print(f"time.time() delta = {t1-t0:10.8f}")


for i in range(10):
    t0 = time.perf_counter()
    t1 = time.perf_counter()
    print(f"time.perf_counter() delta = {t1-t0:10.8f}")

sw = Stopwatch()

sw.start()
N = 1000000
i = 0
while i < N:
    t = time.perf_counter_ns() * 1e-9
    i += 1
sw.stop()
print(f"time.perf_counter_ns    {sw.per_second(N):10.0f}/s")


sw.start()
N = 1000000
i = 0
while i < N:
    t = time.monotonic_ns() * 1e-9
    i += 1
sw.stop()
print(f"time.monotonic_ns       {sw.per_second(N):10.0f}/s")


sw.start()
N = 1000000
i = 0
while i < N:
    t = time.perf_counter()
    i += 1
sw.stop()
print(f"time.perf_counter       {sw.per_second(N):10.0f}/s")


sw.start()
N = 1000000
i = 0
while i < N:
    t = time.monotonic() * 1e-9
    i += 1
sw.stop()
print(f"time.monotonic          {sw.per_second(N):10.0f}/s")
