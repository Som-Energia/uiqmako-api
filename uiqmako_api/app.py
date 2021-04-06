from fastapi import FastAPI

def build_app():
    import config

    app = FastAPI()

    app.settings = config.settings
    return app
