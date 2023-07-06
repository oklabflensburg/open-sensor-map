#!./venv/bin/python

from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()


@app.post('/data/')
async def get_data(data: Request):
    req = await data.json()
    print(req)

    return {
        'status': 'SUCCESS',
        'data': req
    }
