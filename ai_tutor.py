import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import numpy as np


load_dotenv()

# ── Page Config ──────────────────────────────
st.set_page_config(
    page_title = "AI Tutor — by Parfait",
    page_icon  = "🤖",
    layout     = "centered"
)

# ── Header ───────────────────────────────────
st.title("🤖 AI Tutor")
st.caption("Your personal AI learning assistant — Built by Parfait from Rwanda")
st.divider()

# ── API Client ──────────────────────────
client = OpenAI(
    base_url = "https://openrouter.ai/api/v1",
    api_key  = os.getenv("OPENROUTER_API_KEY")
)

# ── System Prompt ────────────────────────────
SYSTEM_PROMPT = """You are a helpful AI tutor for students learning 
Python and AI development. You explain things clearly with examples, 
encourage the student, and relate concepts to real AI industry use cases. 
Keep answers concise but complete."""

# ── Session State — remembers conversation ───
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Display Chat History ─────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── User Input ───────────────────────────────
user_input = st.chat_input("Ask me anything about Python or AI...")

if user_input:
    # show user message
    with st.chat_message("user"):
        st.write(user_input)

    # add to history
    st.session_state.messages.append({
        "role"   : "user",
        "content": user_input
    })

    # call AI
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model    = "openrouter/free",
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *st.session_state.messages
                ],
                max_tokens = 1024
            )
            reply = response.choices[0].message.content
            st.write(reply)

    # save AI reply to history
    st.session_state.messages.append({
        "role"   : "assistant",
        "content": reply
    })
    # Add a sidebar with settings
with st.sidebar:
    st.header("⚙️ Settings")
    subject = st.selectbox(
        "I want to learn about:",
        ["Python Basics", "Machine Learning",
         "Deep Learning", "AI APIs", "Data Science"]
    )
    difficulty = st.radio(
        "My level:",
        ["Beginner", "Intermediate", "Advanced"]
    )
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Update system prompt with selections
SYSTEM_PROMPT = f"""You are an AI tutor. The student wants to learn 
about {subject} at {difficulty} level. Adjust your explanations 
accordingly. Be encouraging and use practical examples."""

#Add Student Data Analysis Feature


# Add a tab for data analysis
tab1, tab2 = st.tabs(["💬 AI Chat", "📊 Student Analysis"])

with tab2:
    st.header("Student Grade Analyzer")

    # file upload
    uploaded = st.file_uploader("Upload student CSV", type="csv")

    if uploaded:
        df = pd.read_csv(uploaded)
        df["average"] = df[["math","science","english"]].mean(axis=1)

        st.dataframe(df)

        # AI analysis of the data
        if st.button("🤖 Get AI Analysis"):
            summary = df.describe().to_string()
            response = client.chat.completions.create(
                model    = "openrouter/free",
                messages = [{
                    "role"   : "user",
                    "content": f"Analyze this student data and give insights:\n{summary}"
                }],
                max_tokens = 500
            )
            st.write(response.choices[0].message.content)