__all__ = [
    "prepare_run_cli",
    "rebuild_final_cli",
    "run_scheduler_cli",
]


def __getattr__(name: str):
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    import importlib

    module = importlib.import_module(f"{__name__}.{name}")
    globals()[name] = module
    return module
