import json
from PyPDF2 import PdfReader
from docx import Document
from google.adk.agents import Agent

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def parse_cv(file_path: str) -> dict:
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return {"status": "error", "msg": "Unsupported file format"}
    return {"raw_text": text}

root_agent = Agent(
    name="cv_parser_agent",
    model="gemini-2.0-flash",
    description="Agent to extract structured data from CVs",
    instruction=(
        "You are a CV parser.\n\n"
        "Step 1: When you receive {'raw_text': '...'}, first extract the following fields from the resume text into JSON:\n"
        "{\n"
        '  \"name\": \"<full name or null>\",\n'
        '  \"email\": \"<email or null>\",\n'
        '  \"phone\": \"<phone or null>\",\n'
        '  \"location\": { \"city\": \"<city or null>\", \"country\": \"<country or null>\" },\n'
        '  \"education\": { \"degree\": \"<degree or null>\", \"university\": \"<university or null>\", \"graduation_year\": <year or null> },\n'
        '  \"experience\": [ { \"role\": \"<role or null>\", \"company\": \"<company or null>\", \"duration\": \"<duration or null>\" } ]\n'
        "}\n\n"
        "Step 2: When the user asks a specific question (like 'What is your phone?', 'Give me location', 'What is your degree?'), "
        "return ONLY that field’s value.\n"
        "   - Example:\n"
        "     User: 'What is your phone?'\n"
        "     Response: '+91-8838900673'\n\n"
        "     User: 'What is your location?'\n"
        "     Response: {\"city\": \"Chennai\", \"country\": \"India\"}\n\n"
        "Step 3: If the user does NOT ask for a specific field, always return the full JSON.\n\n"
        "Always return valid JSON or a plain value (string, object, number) only — no extra explanation."
    ),
    tools=[parse_cv],
)
