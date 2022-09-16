import threading
import queue
from time import sleep

q = queue.Queue()

def worker():
    while True:
        item = q.get()
        print(f'Working on {item}')
        print(f'Finished {item}')
        sleep(1)
        #q.task_done()

# Turn-on the worker thread.
threading.Thread(target=worker, daemon=True).start()

# Send thirty task requests to the worker.
fruits = {
    'apple': 'red',
    'banana': 'yellow',
}
while True:
    q.put(fruits)
    sleep(1)

# Block until all tasks are done.
q.join()
print('All work completed')