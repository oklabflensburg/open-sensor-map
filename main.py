#!./venv/bin/python

from fastapi import FastAPI
from pydantic import BaseModel


class Row(BaseModel):
    name: str
    description: str | None = None
    tax: float | None = None


app = FastAPI()


@app.post('/data/')
async def insert_row(row: Row):
    print(row)
