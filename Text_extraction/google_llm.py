from prompts import TEXT_EXTRACTION_PROMPT, document_classification_prompt, extract_json_prompt
from models import PunishmentLetter, document_models, DocumentClassificationResult

from pydantic import BaseModel
from langchain_groq import ChatGroq
from google import genai
import os


client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY", ""))
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    max_retries=3,
    temperature=0.1,
)


async def get_file_content(file_path: str, template_type: str = None) -> dict | None:
    myfile = client.files.upload(file=file_path)
    llm_with_parser = llm.with_structured_output(PunishmentLetter)
    if template_type:
        llm_with_parser = llm.with_structured_output(document_models.get(template_type, PunishmentLetter))

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=[TEXT_EXTRACTION_PROMPT, myfile]
        )
        extracted_text = response.text
        structured_response = llm_with_parser.invoke(extracted_text)
        print(type(structured_response))

        if isinstance(structured_response, BaseModel):
            return structured_response.model_dump()
        else:
            return structured_response
    except Exception as e:
        print(f"Error generating content: {e}")
        return None
    


async def document_classification(doc_path: str) -> dict:
    myfile = client.files.upload(file=doc_path)
    structured_llm = llm.with_structured_output(DocumentClassificationResult)

    response = client.models.generate_content(
            model="gemini-2.0-flash", contents=[document_classification_prompt, myfile]
        )
    extracted_text = response.text

    response = structured_llm.invoke(extracted_text)

    if isinstance(response, BaseModel):
        return response.model_dump()
    else:
        return {"status": "error", "message": "Invalid response format"}



async def extract_json(doc_path: str, template_type: str = "ProbationLetter", stamp_reference_path: str = "ProjectData//AllMasterStamps-1.pdf") -> dict:
    document_file = client.files.upload(file=doc_path)
    stamp_reference_file = client.files.upload(file=stamp_reference_path)

    structured_llm = llm.with_structured_output(document_models.get(template_type))

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            extract_json_prompt,
            document_file,
            stamp_reference_file
        ]
    )
    
    response = structured_llm.invoke(response.text)

    if isinstance(response, BaseModel):
        return response.model_dump()
    else:
        return {"status": "error", "message": "Invalid response format"}
    