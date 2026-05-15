from typing import Dict, List, Optional

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from core.file_services import FileToolkit


router = APIRouter(prefix="/files", tags=["files"])


class CreateDocumentRequest(BaseModel):
    kind: str
    title: str = "PeacockAI Document"
    content: str = ""
    output_path: Optional[str] = None


class EditTextRequest(BaseModel):
    path: str
    content: Optional[str] = None
    replacements: Optional[Dict[str, str]] = None


class CompressRequest(BaseModel):
    paths: List[str]
    output_path: Optional[str] = None


class ExtractRequest(BaseModel):
    archive_path: str
    output_dir: Optional[str] = None


class ReadFileRequest(BaseModel):
    path: str


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    return FileToolkit.save_upload(file.filename, data)


@router.post("/read")
def read_file(request: ReadFileRequest):
    return FileToolkit.read_file(request.path)


@router.post("/create")
def create_document(request: CreateDocumentRequest):
    return FileToolkit.create_document(
        request.kind,
        request.title,
        request.content,
        request.output_path,
    )


@router.post("/edit-text")
def edit_text(request: EditTextRequest):
    return FileToolkit.edit_text_file(
        request.path,
        content=request.content,
        replacements=request.replacements,
    )


@router.post("/compress")
def compress(request: CompressRequest):
    return FileToolkit.compress(request.paths, request.output_path)


@router.post("/extract")
def extract(request: ExtractRequest):
    return FileToolkit.extract(request.archive_path, request.output_dir)
