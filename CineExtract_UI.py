
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()

st.set_page_config(
    page_title="CineExtract",
    page_icon="🎬",
    layout="wide"
)

# ---------------- UI Styling ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #160f30, #291447, #48184f);
    color: white;
}
.block-container {
    max-width: 1050px;
    padding-top: 2rem;
}
.hero {
    background: linear-gradient(110deg, #ff512f, #dd2476, #7b2ff7);
    padding: 30px;
    border-radius: 22px;
    text-align: center;
    margin-bottom: 25px;
}
.hero h1 {
    color: white;
    font-size: 46px;
    font-weight: 850;
}
.hero p {
    color: #fff0fa;
    font-size: 17px;
}
.stTextArea textarea {
    background: #fffaff !important;
    color: #251333 !important;
    border: 2px solid #d66bdf !important;
    border-radius: 14px !important;
    font-size: 16px !important;
}
.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #ff512f, #dd2476, #7b2ff7);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: bold;
    min-height: 45px;
}
.result-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 22px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Header ----------------

st.markdown("""
<div class="hero">
    <h1>🎬 CineExtract</h1>
    <p>Turn movie paragraphs into structured information with AI</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🍿 Enter your movie paragraph")

para = st.text_area(
    "Movie paragraph",
    height=220,
    placeholder="Paste a paragraph describing a movie here...",
    label_visibility="collapsed"
)

# ---------------- Pydantic Schema ----------------

class Movie(BaseModel):
    title: str
    release_year: Optional[int] = None
    genre: List[str]
    director: Optional[str] = None
    cast: List[str]
    rating: Optional[float] = None
    summary: str

parser = PydanticOutputParser(pydantic_object=Movie)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a movie information extraction assistant.

Analyze the given movie paragraph and extract useful information.
Use only information supported by the paragraph.
Use null for missing optional values and empty lists for missing lists.
Do not invent details.

{format_instructions}
"""),
    ("human", "{paragraph}")
])

# ---------------- Extraction ----------------

if st.button("✨ Extract Movie Information"):
    if not para.strip():
        st.warning("Please enter a movie paragraph first.")

    elif not os.getenv("GEMINI_API_KEY"):
        st.error("GEMINI_API_KEY not found. Check your .env file.")

    else:
        try:
            model = ChatGoogleGenerativeAI(
                model="gemini-3.5-flash-lite",
                google_api_key=os.getenv("GEMINI_API_KEY"),
                max_tokens=500
            )

            with st.spinner("🎥 Analyzing your movie paragraph..."):
                final_prompt = prompt.invoke({
                    "paragraph": para,
                    "format_instructions": parser.get_format_instructions()
                })

                response = model.invoke(final_prompt)

                # FIX: Convert Gemini response content into a string
                content = response.content

                if isinstance(content, list):
                    content = "".join(
                        block.get("text", "")
                        if isinstance(block, dict)
                        else str(block)
                        for block in content
                    )

                # Parse and validate the extracted information
                movie = parser.parse(content)

            st.markdown("---")
            st.markdown("## ✨ Extracted Movie Information")

            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"### 🎞️ {movie.title}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**📅 Release Year**")
                st.write(
                    movie.release_year
                    if movie.release_year is not None
                    else "Not specified"
                )

            with col2:
                st.markdown("**🎭 Genre**")
                st.write(
                    ", ".join(movie.genre)
                    if movie.genre else "Not specified"
                )

            with col3:
                st.markdown("**⭐ Rating**")
                st.write(
                    movie.rating
                    if movie.rating is not None
                    else "Not specified"
                )

            st.markdown("**🎬 Director**")
            st.write(movie.director or "Not specified")

            st.markdown("**🌟 Cast**")
            st.write(
                ", ".join(movie.cast)
                if movie.cast else "Not specified"
            )

            st.markdown("**📝 Quick Summary**")
            st.write(movie.summary or "Not specified")

            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Extraction failed: {e}")

st.markdown("---")
st.caption("🎬 CineExtract | Powered by LangChain, Pydantic & Gemini")
