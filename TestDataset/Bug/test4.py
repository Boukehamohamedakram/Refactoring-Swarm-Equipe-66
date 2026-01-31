import threading
import time

class Scheduler:
    def __init__(self):
        self.tasks = []

    def add_task(self, task, queue=[]):
        queue.append(task)
        self.tasks.append(task)
        if len(queue) > 3:
            print("Queue overloaded!")
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
        print(f"Executing {task}")

scheduler = Scheduler()
scheduler.add_task("Task1")
scheduler.add_task("Task2")
scheduler.add_task("Task3")
scheduler.add_task("Task4")
scheduler.run_tasks()