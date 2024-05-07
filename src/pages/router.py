#from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from src.routes.auth import signup


router = APIRouter(
    prefix="/pages",
    tags=["pages"]
)
#BASE_DIR = Path(__file__).parent
templates =  Jinja2Templates(directory="src/templates")
#templates = Jinja2Templates(directory=BASE_DIR /  "templates")

@router.get("/base")
def get_base_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/search/{operation_type}")
def get_search_page(request: Request, operations=Depends(signup)):
    return templates.TemplateResponse("search.html", {"request": request,"operations": operations["new_user"]})


# @router.get("/search")
# def get_search_page(request: Request):
#     return templates.TemplateResponse("search.html", {"request": request})

