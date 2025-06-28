TEXT_EXTRACTION_PROMPT = """You are a highly skilled text extraction model.
Your task is to extract relevant information from the provided file.
"""

PARSING_PROMPT = """You are an expert in extracting information from text. 
Your task is to extract specific details from the provided text. 
The text may contain various types of information, including but not limited to
names, dates, locations, and other relevant data."""



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

3. **Translate**:
    - If you find any TELUGU text in the data transilate into ENGLISH

**Important rules**:
- Do NOT guess or hallucinate missing text.
- Use only what's visible in the document image.
- Populate every field from the schema, even if text are missing (use `None` then).
"""


DOCUMENT_DESCRIPTION = {
"PunishmentLetter": "It contains R.C No followed By D.O No and date. It describes the punishment awarded and officer sign who awarded the punishment.",
"EarnedLeaveLetter": "It contails R.C No followed by HOD No and date. It is of a format mail with Subject, Reference and Order each containing crutial information. At last it is stamped (with details like officer position, location and rank) and addressed to higher officer followed by Administrative officer sign.",
"RewardLetter": "It consists of R.C No, H O O No followed by Date an stamp. Order details start: First Subject followed by Reference with order no. Next it contains Rewards awarded to officers along with their ranks. At last signed by HOD along with location and To address",
"MedicalLeave": "It starts with a stamp containing unit, district followed by rank, coy and address. Next Subject and Reason for Leave. Next it is addressed to Higher officier along with sigh of officer with date.",
"ProbationLetter": """
        The document is structured into two main parts:

        Page 1, you'll find the "Register of Probationer" which provides administrative information such as his service class category , name , date of regularization , prescribed probation period , and the official completion date of his probation. This page also lists any leave taken , tests to be passed , punishments , pending inquiries , and character and conduct assessment. Remarks from the I/C Officer , Commandant , and DIG  regarding his probation completion are also present here, culminating in the orders from the Addl. Director General of Police.

        Pages 2 and 3 comprise "FORM - A," a Probation Special Confidential Report. Here, you can find personal details like his date of birth , salary information , and qualifications. This section also details the acceptance of his self-appraisal report and an assessment of his performance during the year. The document concludes with the reporting officer's details (name, designation, and date) , the countersigning officer's remarks (including their name, designation, and date) , and the final opinion of the Head of the Department, including their signature, name, designation, and the date the probation was declared
    """
}