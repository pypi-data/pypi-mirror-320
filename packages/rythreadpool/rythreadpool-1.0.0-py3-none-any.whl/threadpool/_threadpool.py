from threading import Thread, Semaphore
import sys

class ThreadPool:
    def __init__(self, size):
        self._size = size
        self._jobs = []

        self._mutex = Semaphore(1)
        self._threadCount = 0

    def execute(self, fn, args):
        if not isinstance(args, tuple):
            raise TypeError(f'"args" parameter must be a tuple, but "{type(args)}" found')

        self._mutex.acquire()
        self._jobs.append((fn, args))

        if self._threadCount < self._size:
            self._threadCount += 1
            Thread(target=self._runner, args=()).start()

        self._mutex.release()

    def _runner(self):
        while True:
            self._mutex.acquire()

            if not self._jobs:
                self._threadCount -= 1

                self._mutex.release()
                return

            fn, args = self._jobs.pop(0)
            self._mutex.release()

            try:
                fn(*args)

            except Exception as e:
                print(f'Threaded execution of function "{fn.__name__}" failed because of: {e}', file=sys.stderr)

    def isWorking(self):
        self._mutex.acquire()
        working = self._threadCount != 0

        self._mutex.release()
        return working