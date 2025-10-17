import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Resume Critiquer", page_icon=":memo:", layout="centered")

st.title("AI Resume Critiquer")
st.markdown("Upload your resume in PDF format, and get AI-powered feedback to improve it!")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf","txt"])

job_role = st.text_input("Enter the job role you are applying for (optional):")

analyze = st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text
    

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")


if analyze and uploaded_file:
    st.info("Analyzing the resume, please wait...")
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("The uploaded file is empty ...")
            st.stop()

        prompt = f"""Provide detailed feedback on the following resume content to help improve it for a job application
        for the role of '{job_role if job_role else 'general job applications'}'. Focus on the structure, clarity, relevance of experience, and skills alignment. give specific improments for {job_role if job_role else 'general job applications'}.
        Resume Content:
        {file_content}

        please provide your feedback in markdown format."""

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert career advisor with years of experience in HR and recruitment."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
        )

        st.markdown("### Analysis Result:")
        st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
