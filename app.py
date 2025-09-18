import os, streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Interview Qs", page_icon="🧠")
st.title("🧠 Interview Question Generator")

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

role = st.text_input("Role title")
region = st.selectbox("Region (legal context)", ["US","UK/EU"])
jd = st.file_uploader("Upload JD (txt/docx/pdf)", type=["txt","docx","pdf"])

def read_text(file):
    ext = (file.name.rsplit(".",1)[-1] or "").lower()
    if ext == "txt":
        return file.read().decode("utf-8", errors="ignore")
    try:
        if ext == "docx":
            import docx
            return "\n".join([p.text for p in docx.Document(file).paragraphs])
        if ext == "pdf":
            import pypdf
            r = pypdf.PdfReader(file)
            return "\n".join([p.extract_text() or "" for p in r.pages])
    except Exception:
        return ""
    return ""

if st.button("Generate", disabled=not (role or jd)):
    with st.spinner("Generating..."):
        jd_text = read_text(jd) if jd else ""
        prompt = f"""You are a senior TA partner.
Generate structured, job-relevant, legally-safe interview questions in clear Markdown.
Use bold section headers and bullet points. Avoid discriminatory topics.
Region: {region}. Role: {role or 'Not specified'}.
Job Description (may be empty): {jd_text[:7000]}
"""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.4,
        )
        st.markdown(resp.choices[0].message.content)
