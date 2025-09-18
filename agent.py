import re
import json
from PyPDF2 import PdfReader
from docx import Document
from google.adk.agents import Agent

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def parse_cv(file_path: str) -> dict:
    """Parses CV and extracts name, phone, email, education (college & location)."""
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return {"status": "error", "msg": "Unsupported file format"}

    
    email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)
    phone = re.findall(r"\+?\d[\d\s-]{8,15}", text)

    
    college_match = re.search(r"(SRM.*|IIT.*|NIT.*|University.*|College.*)", text, re.I)

    
    location_match = re.search(r"(Chennai|Bangalore|Hyderabad|Delhi|Mumbai|India)", text, re.I)

    result = {
        "name": text.split("\n")[0].strip(),  
        "email": email[0] if email else None,
        "phone": phone[0] if phone else None,
        "education": {
            "college": college_match.group(1).strip() if college_match else None,
            "location": location_match.group(1) if location_match else None
        },
        "raw_text_preview": text[:500]  
    }

    return {"status": "success", "cv_data": result}

root_agent = Agent(
    name="cv_parser_agent",
    model="gemini-2.0-flash",
    description="Agent to extract structured data from CVs",
    instruction="You are a CV parser. Extract name, email, phone, and education details into JSON.",
    tools=[parse_cv],
)
