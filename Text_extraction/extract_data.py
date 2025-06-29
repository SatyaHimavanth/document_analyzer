from models import document_models, DocumentClassificationResult
from prompts import extract_json_prompt, document_classification_prompt, DOCUMENT_DESCRIPTION

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI

from pydantic import BaseModel, Field
import base64
import fitz
import os
import io


from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

langfuse = Langfuse(
  secret_key="sk-lf-d54c76d6-6c46-425c-b1ea-211256dcea06",
  public_key="pk-lf-7065a313-db9f-4bc3-b6ad-0e1e68cd0a61",
  host="http://20.102.104.3:3000"
)

langfuse_handler = CallbackHandler()

# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
llm = AzureChatOpenAI(
    deployment_name="gpt-4o",
    model="gpt-4o",
    temperature=0.0,
    api_version="2025-01-01-preview"
)



def load_file_as_base64(path: str) -> dict:
    
    mimetype = "application/pdf" if path.endswith(".pdf") else "image/jpg"
    message_content = []

    if mimetype == "application/pdf":
        doc = fitz.open(path)
        images = []
        for page in doc:
            pix = page.get_pixmap(dpi=150)
            buffer = io.BytesIO(pix.tobytes("png"))
            base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            images.append(base64_str)
        doc.close()
        total_pages = len(images)
        for i, img in enumerate(images, start=1):
            message_content.append({
                "type": "text",
                "text": f"Page {i} of {total_pages}"
            })

            # Add image to message
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img}"
                }
            })
    else:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpg;base64,{encoded}"
                }
            })
    return message_content



async def document_classification(doc_path: str) -> dict:
    structured_llm = llm.with_structured_output(DocumentClassificationResult)
            
    file_content = load_file_as_base64(doc_path)
    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": document_classification_prompt},
        ] + file_content,
    }
    response = structured_llm.invoke([message], config={"callbacks": [langfuse_handler]})

    if isinstance(response, BaseModel):
        return response.model_dump()
    else:
        return {"status": "error", "message": "Invalid response format"}


async def extract_json(doc_path: str, document_type: str = "ProbationLetter", stamp_reference_path: str = "ProjectData//AllMasterStamps-1.pdf") -> dict:
    
    document_image = load_file_as_base64(doc_path)
    stamp_reference_image = load_file_as_base64(stamp_reference_path)
    
    structured_llm = llm.with_structured_output(document_models.get(document_type))
    
    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": extract_json_prompt},
            {"type": "text", "text": DOCUMENT_DESCRIPTION[document_type]}
        ]  + document_image + stamp_reference_image,
    }
    
    response = structured_llm.invoke([message], config={"callbacks": [langfuse_handler]})

    if isinstance(response, BaseModel):
        return response.model_dump()
    else:
        return {"status": "error", "message": "Invalid response format"}
    