from queue import Queue

_jobs = Queue()


def enqueue(job):
    _jobs.put(job)


def dequeue():
    return _jobs.get()


def task_done():
    _jobs.task_done()


def size():
    return _jobs.qsize()
