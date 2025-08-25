import os
import io
from datetime import date
import streamlit as st
from dotenv import load_dotenv
from docx import Document
from docx.shared import Pt, Inches

import google.generativeai as genai

load_dotenv()

st.set_page_config(page_title="AI Resume & Cover Letter Generator", page_icon="🧠", layout="wide")

# --- Helpers ---
def get_api_key():
    return os.getenv("GEMINI_API_KEY") or st.session_state.get("api_key_sidebar", "")

def get_model(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

def call_llm(model, system_prompt: str, user_content: str) -> str:
    prompt = f"{system_prompt}\n\n---\n{user_content}".strip()
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        st.error(f"LLM error: {e}")
        return ""

def make_docx_from_text(text: str, filename="output.docx"):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    for line in text.splitlines():
        doc.add_paragraph(line)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- UI ---
st.title("🧠 AI Resume & Cover Letter Generator")
st.caption("Built with Streamlit + Gemini (no RAG)")

with st.sidebar:
    st.header("Settings")
    st.text_input("Gemini API Key", type="password", key="api_key_sidebar")
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Concise"], index=0)

st.subheader("Candidate Details")
name = st.text_input("Full Name")
title = st.text_input("Headline / Title", placeholder="e.g., ML Engineer | Data Scientist")
contact = st.text_input("Contact (email | phone | links)")
summary = st.text_area("Professional Summary")
skills = st.text_area("Skills (comma-separated)")
experience = st.text_area("Experience")
projects = st.text_area("Projects")
education = st.text_input("Education")

# Prompts
RESUME_SYS = f"""
You are an expert resume writer.
Write a one-page resume in clean Markdown.
Include: Name, Title, Contact, Summary, Skills, Experience, Projects, Education.
Tone: {tone}.
Output only markdown.
"""

COVER_SYS = f"""
You are a professional cover letter writer.
Write a short cover letter tailored to the candidate.
Tone: {tone}.
Output plain text only.
"""

# Actions
api_key = get_api_key()
make_resume = st.button("✨ Generate Resume")
make_cover = st.button("📝 Generate Cover Letter")

user_blob = f"""
Name: {name}
Title: {title}
Contact: {contact}
Summary: {summary}
Skills: {skills}
Experience: {experience}
Projects: {projects}
Education: {education}
""".strip()

if api_key:
    model = get_model(api_key)

if make_resume and api_key:
    st.subheader("📄 Resume Preview")
    resume_md = call_llm(model, RESUME_SYS, user_blob)
    st.markdown(resume_md)
    st.download_button("⬇️ Download Resume (.docx)", make_docx_from_text(resume_md), "resume.docx")

if make_cover and api_key:
    st.subheader("✉️ Cover Letter Preview")
    cover_txt = call_llm(model, COVER_SYS, user_blob)
    st.text(cover_txt)
    st.download_button("⬇️ Download Cover Letter (.docx)", make_docx_from_text(cover_txt), "cover_letter.docx")