import asyncio

from desktop_app.src.utils import setup_logger

logger = setup_logger(__name__)


class BackgroundTaskManager:
    def __init__(self):
        self.tasks = []

    async def add_task(self, coroutine):
        task = asyncio.create_task(coroutine)
        self.tasks.append(task)
        task.add_done_callback(self.task_done)

    def task_done(self, task):
        self.tasks.remove(task)
        if task.exception():
            logger.error(f"Background task failed: {task.exception()}")

    async def run_periodic_task(self, coroutine, interval_seconds):
        while True:
            try:
                await coroutine()
            except Exception as e:
                logger.error(f"Periodic task failed: {e}")
            await asyncio.sleep(interval_seconds)

    def start_periodic_task(self, coroutine, interval_seconds):
        self.add_task(self.run_periodic_task(coroutine, interval_seconds))

    async def wait_for_all_tasks(self):
        await asyncio.gather(*self.tasks, return_exceptions=True)
