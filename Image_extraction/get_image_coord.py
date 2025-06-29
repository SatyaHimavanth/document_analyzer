from pydantic import BaseModel, Field
from typing import List, Literal
from Text_extraction.google_llm import get_file_coordinates

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI

from PIL import Image
import base64
import fitz
import io
import os


llm = AzureChatOpenAI(
    deployment_name="gpt-4o",
    model="gpt-4o",
    temperature=0.0,
    api_version="2025-01-01-preview"
)


class StampCoordinate(BaseModel):
    page_number: int = Field(..., description="Page number where stamp is found (1-indexed)")
    x: int = Field(..., description="Top-left x-coordinate of stamp in pixels")
    y: int = Field(..., description="Top-left y-coordinate of stamp in pixels")
    width: int = Field(..., description="Width of the stamp region in pixels")
    height: int = Field(..., description="Height of the stamp region in pixels")
    confidence: float = Field(..., description="Confidence score of detection, between 0 and 1")

class StampDetectionResult(BaseModel):
    document_type: Literal["pdf", "image"]
    filename: str
    stamp_coordinates: List[StampCoordinate]



def extract_stamps_from_image(image_path: str, coords: List[StampCoordinate], save_dir: str = "stamps") -> List[str]:
    os.makedirs(save_dir, exist_ok=True)
    original = Image.open(image_path)
    file_name = os.path.basename(image_path)
    saved_paths = []

    for i, coord in enumerate(coords, 1):
        left = coord.x
        top = coord.y
        right = coord.x + coord.width
        bottom = coord.y + coord.height

        cropped = original.crop((left, top, right, bottom))
        out_path = os.path.join(save_dir, f"{file_name}_stamp_{i}.png")
        cropped.save(out_path)
        saved_paths.append(out_path)

    return saved_paths


def extract_stamps_from_pdf(pdf_path: str, coords: List[StampCoordinate], save_dir="stamps") -> List[str]:
    os.makedirs(save_dir, exist_ok=True)
    file_name = os.path.basename(pdf_path)
    saved_paths = []

    # Open the PDF using fitz (PyMuPDF)
    doc = fitz.open(pdf_path)
    
    for i, coord in enumerate(coords):
        page_index = coord.page_number - 1
        if page_index >= len(doc):
            continue

        page = doc[page_index]
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))

        # Crop the stamp
        cropped = img.crop((
            coord.x,
            coord.y,
            coord.x + coord.width,
            coord.y + coord.height
        ))

        out_path = os.path.join(save_dir, f"{file_name}_stamp_page{coord.page_number}_{i+1}.png")
        cropped.save(out_path)
        saved_paths.append(out_path)

    doc.close()
    return saved_paths


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


async def run_stamp_detection(file_path: str, stamp_reference_path: str = "ProjectData//AllMasterStamps-1.pdf"):
    filename = os.path.basename(file_path)
    # messages = load_file_as_base64(file_path)
    # stamp_reference_image = load_file_as_base64(stamp_reference_path)

    # llm_structured = llm.with_structured_output(StampDetectionResult)
    # prompt_extra1 = [{"type": "text", "text": "Here are few example stamps. Please use these as reference"},
    #                  {"type": "text", "text": "Please verify the coordinates by superimposing before sending coordinates."}]

    # message = {
    #     "role": "user",
    #     "content": [
    #         {"type": "text", "text": "You're an expert in identifying stamps on documents. Please extract all the available stamps from the given file or image"},
    #     ]  + messages + prompt_extra1 + stamp_reference_image
    # }
    # response = llm_structured.invoke([message])

    coordinates = await get_file_coordinates(file_path)

    print(coordinates)

    stamp_save_paths = []
    if filename.endswith(".pdf"):
        stamp_save_paths = extract_stamps_from_pdf(file_path, coordinates.stamp_coordinates)
    else:
        stamp_save_paths = extract_stamps_from_image(file_path, coordinates.stamp_coordinates)

    return stamp_save_paths


# result = await run_stamp_detection(r"C:\Users\hp\Downloads\USE CASE Number-6(Doc to Data)\DOCUMENT INFORMATION TEMPLATES\Reward Letter\Reward Letter sample_2.jpg")
# print(result)

import asyncio
result = asyncio.run(run_stamp_detection(r"C:\Users\hp\Downloads\USE CASE Number-6(Doc to Data)\DOCUMENT INFORMATION TEMPLATES\Reward Letter\Reward Letter sample_2.jpg"))
print(result)