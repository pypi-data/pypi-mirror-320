from __future__ import annotations

import asyncio
import logging
from multiprocessing import Event, Process

import zmq.asyncio
from client import Client
from scheduler import Scheduler
from worker import Worker


def init_logging():
    logging.basicConfig(level=logging.INFO)


def init_event_loop():
    loop = zmq.asyncio.ZMQEventLoop()
    asyncio.set_event_loop(loop)
    return loop


def init_tea_client(stop_event):  # noqa:ARG001
    init_logging()

    async def create_work(loop):
        client = Client(loop=loop)
        N = 10
        MSG_SIZE = 1_000
        for _ in range(N):
            # if i % 1 == 0:
            # print(f"[ Tea Client  ] {i+1} jobs submitted")
            await client.submit(b"hello.world.tea", [b"o" * MSG_SIZE])

        for _ in range(N):
            service, message = await client.get()
            # if i % 1 == 0:
            # print(f"[ Tea Client  ] {i+1} jobs completed")

        # print("[ Client  ] === DONE ===")
        client.disconnect()

    loop = init_event_loop()
    loop.run_until_complete(create_work(loop))


def init_coffee_client(stop_event):  # noqa:ARG001
    init_logging()

    async def create_work(loop):
        client = Client(loop=loop)
        N = 10
        MSG_SIZE = 1_000
        for _ in range(N):
            # if i % 1 == 0:
            # print(f"[ Tea Client  ] {i+1} jobs submitted")
            await client.submit(b"hello.world.coffee", [b"o" * MSG_SIZE])

        for _ in range(N):
            service, message = await client.get()
            # if i % 1 == 0:
            # print(f"[ Coffee Client  ] {i+1} jobs completed")

        # print("[ Client  ] === DONE ===")
        client.disconnect()

    loop = init_event_loop()
    loop.run_until_complete(create_work(loop))


def init_scheduler(stop_event):
    init_logging()
    scheduler = Scheduler(stop_event, loop=init_event_loop())
    scheduler.run()


def init_tea_worker(stop_event):
    counter = 0

    async def hello_world_worker(*message):  # noqa:ARG001
        nonlocal counter
        counter += 1
        # # print(f"[ Tea  Worker  ] processing message {counter}")
        return (b"1", b"2", b"3")

    init_logging()
    loop = init_event_loop()
    worker = Worker(stop_event, loop=loop)
    loop.run_until_complete(worker.run(b"hello.world.tea", hello_world_worker))


def init_coffee_worker(stop_event):
    counter = 0

    async def hello_world_worker(*message):  # noqa:ARG001
        nonlocal counter
        counter += 1
        # print(f"[ Coffee Worker  ] processing message {counter}")
        return (b"1", b"2", b"3")

    init_logging()
    loop = init_event_loop()
    worker = Worker(stop_event, loop=loop)
    loop.run_until_complete(worker.run(b"hello.world.coffee", hello_world_worker))


if __name__ == "__main__":
    NUM_CLIENTS = 4
    NUM_WORKERS = 4

    stop_event = Event()
    worker_processes = [
        Process(target=init_tea_worker, args=(stop_event,)) for _ in range(NUM_WORKERS)
    ] + [
        Process(target=init_coffee_worker, args=(stop_event,))
        for _ in range(NUM_WORKERS)
    ]
    for worker in worker_processes:
        worker.start()

    scheduler_process = Process(target=init_scheduler, args=(stop_event,))
    scheduler_process.start()

    client_processes = [
        Process(target=init_tea_client, args=(stop_event,)) for _ in range(NUM_CLIENTS)
    ] + [
        Process(target=init_coffee_client, args=(stop_event,))
        for _ in range(NUM_CLIENTS)
    ]
    for client in client_processes:
        client.start()
