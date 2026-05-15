from fastapi import APIRouter


router = APIRouter()


@router.get("/agents")
def agents():

    return {

        "agents": [

            "planner",

            "coder",

            "reviewer",

            "critic"
        ]
    }