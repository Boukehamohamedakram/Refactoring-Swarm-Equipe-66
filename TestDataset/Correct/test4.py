import threading
import time

class Scheduler:
    def __init__(self):
        self.tasks = []
        self.lock = threading.Lock()  # Fix concurrency

    def add_task(self, task, queue=None):
        # Fix mutable default argument
        if queue is None:
            queue = []

        # Input validation
        if not isinstance(task, str):
            raise TypeError("task must be a string")

        queue.append(task)
        with self.lock:
            self.tasks.append(task)

        # Removed print to separate output from function logic
        return queue

    def run_tasks(self):
        threads = []
        for t in self.tasks:
            th = threading.Thread(target=self._execute_task, args=(t,))
            threads.append(th)
            th.start()
        for th in threads:
            th.join()

    def _execute_task(self, task):
        time.sleep(0.1)
        # Printing outside critical logic is okay for demonstration
        print(f"Executing {task}")

scheduler = Scheduler()
scheduler.add_task("Task1")
scheduler.add_task("Task2")
scheduler.add_task("Task3")
scheduler.add_task("Task4")
scheduler.run_tasks()