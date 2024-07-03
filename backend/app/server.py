import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


from src.main import chain
from langchain_core.pydantic_v1 import BaseModel


class Question(BaseModel):
    __root__: str


chain = chain.with_types(input_type=Question)
add_routes(
    app,
    chain.with_types(input_type=dict, output_type=str),
    playground_type='chat'
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
