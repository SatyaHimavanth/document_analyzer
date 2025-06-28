TEXT_EXTRACTION_PROMPT = """You are a highly skilled text extraction model.
Your task is to extract relevant information from the provided file.
"""

PARSING_PROMPT = """You are an expert in extracting information from text. 
Your task is to extract specific details from the provided text. 
The text may contain various types of information, including but not limited to
names, dates, locations, and other relevant data."""


extract_json_prompt = """
You are a document extraction and analysis expert. Your task is to understand layout and extract data 
from the given document image (or PDF) according to a predefined schema.
You are also given a separate reference image that contains known stamp names.

Your tasks:

1. **Extract fields** from the document:
    - For each field in the schema, provide the extracted text from document (or `None` if not found), a confidence score (0.0 to 1.0), and whether the text is `machine_printed` or `handwritten`.

2. **Detect stamps**:
    - If you find any stamp in the document image that matches a stamp from the reference image, copy its **name** into the respective `stampX` field (e.g., `stamp1`, `stamp2`, etc.).
    - If a stamp is **not** present, return `None`.

**Important rules**:
- Do NOT guess or hallucinate missing text.
- Use only what's visible in the document image.
- Populate every field from the schema, even if text are missing (use `None` then).
"""

document_classification_prompt = """
You are an expert in extracting text and analyzing official documents from police departments and other administrative sources.

Your tasks:

1. **Classify the document** into one of the following types based on its content:
   - PunishmentLetter
   - EarnedLeaveLetter
   - RewardLetter
   - MedicalLeave
   - ProbationLetter

2. **Output format**:
   - `document_type`: the most probable document type from the above list
   - `confidence`: confidence score (0.0 to 1.0) for the classification
   - `extracted_text`: list of relevant textual segments extracted from the document, each with:
     - `text`: the actual content
     - `confidence`: how confidently the text was extracted
     - `text_type`: whether the text is `machine_printed` or `handwritten`

**Rules**:
- Do not guess or hallucinate content that is not present in the document.
- If you're unsure about classification, still pick the closest type based on structure and content, and lower the confidence.
- Your classification should be based on patterns like keywords (e.g., "punishment awarded", "earned leave", "reward of ₹", etc.), form layout, and purpose indicators.

You will receive the document as an image or PDF. Analyze only what you see.
"""
