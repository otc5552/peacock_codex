from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from backend.runtime_api import router as runtime_router
from backend.agent_api import router as agent_router
from backend.memory_api import router as memory_router
from backend.model_api import router as model_router
from backend.project_api import router as project_router
from backend.file_api import router as file_router
from backend.media_api import router as media_router
from backend.search_api import router as search_router


app = FastAPI()


app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.include_router(runtime_router)
app.include_router(agent_router)
app.include_router(memory_router)
app.include_router(model_router)
app.include_router(project_router)
app.include_router(file_router)
app.include_router(media_router)
app.include_router(search_router)


@app.get("/")
def home():

    return {

        "message":

        "🔥 PeacockAI Runtime Active"
    }
