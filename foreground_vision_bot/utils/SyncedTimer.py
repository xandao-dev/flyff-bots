import time

class SyncedTimer:
    """
    It turns a function into callable class that will execute only after a certain amount of time.
    Example:
        def print_world(msg):
            print(f"World {msg}")
            time.sleep(2)
        
        print_world_timer = SyncTimer(print_world, 5)
        while True:
            print_world_timer('!!!')
            print("Hello")
            time.sleep(1)
    
    It will print "Hello" every second, but "World !!!" only after 5 seconds. 
    In addition, it will wait 2 seconds before printing "Hello" again, because the function is blocking.
    """
    def __init__(self, func, wait_seconds):
        self.initial_time = time.time()
        self.func = func
        self.wait_seconds = wait_seconds

    def __call__(self, *args, **kwargs):
        if time.time() - self.initial_time > self.wait_seconds:
            self.func(*args, **kwargs)
            self.reset()

    def reset(self):
        self.initial_time = time.time()
