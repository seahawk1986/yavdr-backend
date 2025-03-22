import asyncio
from collections.abc import AsyncIterator
from typing import TypeVar

# https://gist.github.com/antonagestam/8476ada7d74cce93af0339cf32c62ae2?permalink_comment_id=4979924

T = TypeVar("T")
R = TypeVar("R")


async def read_into_queue(
    task: AsyncIterator[T],
    r_type: R,
    queue: asyncio.Queue[tuple[T, R]],
    done: asyncio.Semaphore,
) -> None:
    async for item in task:
        await queue.put((item, r_type))
    # All items from this task are in the queue, decrease semaphore by one.
    await done.acquire()


async def join(*generators: tuple[AsyncIterator[T], R]) -> AsyncIterator[tuple[T, R], None]:
    queue: asyncio.Queue[tuple[T, R]] = asyncio.Queue(maxsize=1)
    done_semaphore = asyncio.Semaphore(len(generators))
    
    # Read from each given generator into the shared queue.
    produce_tasks = [
        asyncio.create_task(read_into_queue(task, r_type, queue, done_semaphore))
        for task, r_type in generators
    ]

    # Read items off the queue until it is empty and the semaphore value is down to zero.
    while not done_semaphore.locked() or not queue.empty():
        try:
            yield await asyncio.wait_for(queue.get(), .001)
        except TimeoutError:
            continue

    # Not strictly needed, but usually a good idea to await tasks, they are already finished here.
    try:
        await asyncio.wait_for(asyncio.gather(*produce_tasks), 0)
    except TimeoutError:
        raise NotImplementedError("Impossible state: expected all tasks to be exhausted")


# ---


