def is_running_on_beam():
    try:
        from beam import env
        return env.is_remote()
    except (ImportError, RuntimeError):
        return False
