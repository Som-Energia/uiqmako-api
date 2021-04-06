# -*- coding: utf-8 -*-
import uvicorn
from uiqmako_api.app import build_app

def main():

    app = build_app()
    uvicorn.run("uiqmako_api.main:app")

if __name__ == '__main__':
    main()
