import threading
import time

finished = threading.Event()
def fun():
    print ("Starting fun")
    finished.set()
    time.sleep(5)

    
start_time = threading.Timer(5,fun)
start_time.start()

while True:
    if finished.is_set():
        start_time.join()
        finished.clear()
    print("Hello")
    time.sleep(1)
