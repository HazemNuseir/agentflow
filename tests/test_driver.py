def run_sync(coro):
    """Execute coroutine synchronously without event loop timers."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value
    raise RuntimeError("Coroutine suspended unexpectedly")

async def sample():
    return {"status": "success", "val": 123}

print("RUN SYNC RESULT:", run_sync(sample()))
