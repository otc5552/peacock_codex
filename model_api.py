from fastapi import APIRouter


router = APIRouter()


@router.get("/models")
def models():

    return {

        "models": [

            "qwen",

            "deepseek",

            "sdxl"
        ]
    }