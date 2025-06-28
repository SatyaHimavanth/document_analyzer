from models import document_models, DocumentClassificationResult
from prompts import extract_json_prompt, document_classification_prompt

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import base64
import os


llm = ChatOpenAI(model="gpt-4o", temperature=0)
# client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY", ""))
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)


def load_file_as_base64(path: str) -> dict:
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    mimetype = "application/pdf" if path.endswith(".pdf") else "image/jpeg"
    type = "file" if path.endswith(".pdf") else "image"
    return {
        "type": type,
        "source_type": "base64",
        "data": encoded,
        "mime_type": mimetype
    }


async def document_classification(doc_path: str) -> dict:
    structured_llm = llm.with_structured_output(DocumentClassificationResult)

    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": document_classification_prompt},
            load_file_as_base64(doc_path)
        ],
    }
    response = structured_llm.invoke([message])

    if isinstance(response, BaseModel):
        return response.model_dump()
    else:
        return {"status": "error", "message": "Invalid response format"}



async def extract_json(doc_path: str, template_type: str = "ProbationLetter", stamp_reference_path: str = "ProjectData//AllMasterStamps-1.pdf") -> dict:

    document_image = load_file_as_base64(doc_path)
    stamp_reference_image = load_file_as_base64(stamp_reference_path)

    structured_llm = llm.with_structured_output(document_models.get(template_type))

    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": extract_json_prompt},
            load_file_as_base64(document_image),
            load_file_as_base64(stamp_reference_image)
        ],
    }
    
    response = structured_llm.invoke([message])

    if isinstance(response, BaseModel):
        return response.model_dump()
    else:
        return {"status": "error", "message": "Invalid response format"}
    