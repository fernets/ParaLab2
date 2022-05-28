from time import sleep
from datetime import datetime
from threading import Thread


class WorkerThread(Thread):
    def run(queue):
        while True:
            item = queue.get()
            if not item is None:
                res = item.func(item.arg)
                item.future.setResult(res)
            if queue.work == False:
                return


class FutureResult:
    def __init__(self):
        self.res = None
        self.hasResult = False

    def setResult(self, res):
        self.res = res
        self.hasResult = True

    def result(self):
        while not self.hasResult:
            pass
        return self.res


class WorkItem:
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg
        self.inWork = False
        self.future = FutureResult()

    def __str__(self):
        return str(self.future.res)


class CustomExecutor:
    def __init__(self, max_workers=4):
        self.thr = []
        self.queue = []
        self.work = True

        if max_workers <= 0:
            raise ValueError("Number of workers can't be <= 0 !")
        for i in range(max_workers):
            self.thr.append(Thread(target=WorkerThread.run, args=[self], daemon=True))
            self.thr[-1].start()

    def execute(self, func, arg):
        i = WorkItem(func, arg)
        self.queue.append(i)
        return i

    def map(self, func, args_array):
        res = []
        for i in args_array:
            res.append(self.execute(func, i))
        return res

    def shutdown(self):
        while True:
            if True in [i.future.hasResult for i in self.queue]:
                self.work = False
                [i.join() for i in self.thr]
                return

    def get(self):
        for i in self.queue:
            if not i.inWork:
                i.inWork = True
                return i


def longTask(x):
    sleep(2)
    return x * 2


exec = CustomExecutor(max_workers=2)
futures = exec.map(longTask, [1, 2, 3, 4])
for f in futures:
    print(f"{datetime.now().strftime('%H:%M:%S')} - {f.future.result()}")
exec.shutdown()
