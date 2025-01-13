from fastapi import FastAPI
from pkb.utils.app import getApp

def app():
    # _api = FastAPI()

    # @_api.get("/")
    # async def root():
    #     return {"message": "Hello World"}

    # return _api

    _app = getApp()
    return _app

def main():
    import uvicorn
    uvicorn.run(app(), host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

