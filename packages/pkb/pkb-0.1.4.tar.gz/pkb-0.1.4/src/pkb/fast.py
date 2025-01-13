from fastapi import FastAPI
from pkb.utils.app import getApp
from dotenv.main import load_dotenv
load_dotenv()

def app():
    _app = getApp()
    return _app

def main():
    import uvicorn
    uvicorn.run(app(), host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

