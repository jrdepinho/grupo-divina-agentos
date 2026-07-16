import threading
import traceback

from app.runtime.agentos.queue import (
    dequeue,
    task_done,
)


class AgentWorker(threading.Thread):

    daemon = True

    def run(self):

        while True:

            print("[WORKER] aguardando job...", flush=True)

            job = dequeue()

            print("[WORKER] job recebido", flush=True)

            try:
                job()

                print("[WORKER] job concluído", flush=True)

            except Exception:
                traceback.print_exc()

            finally:
                task_done()


_worker = AgentWorker()


def start_worker():

    if not _worker.is_alive():
        _worker.start()
