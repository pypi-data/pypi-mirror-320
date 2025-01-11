__version__ = "0.1.2"


from fastapi import FastAPI


def install(app: FastAPI) -> None:
    try:
        from fastapi_extra import routing as native_routing  # type: ignore
        from fastapi_extra import dependency
        
        native_routing.install(app)
        app.dependency_overrides |= dependency.default_dependency_override
    except ImportError:  # pragma: nocover
        pass
