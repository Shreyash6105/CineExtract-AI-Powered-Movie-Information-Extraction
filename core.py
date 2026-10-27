import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    max_tokens=200
)

prompt = ChatPromptTemplate.from_messages(
[("system",
"""
You are a movie information extraction assistant.

Analyze the given movie paragraph and extract useful information.

Extract these fields:
- Movie Name
- Release Year
- Genre
- Director
- Cast
- Main Characters
- Language
- Country
- Runtime
- Production Company
- Music Director
- Rating
- Quick Summary (2-3 sentences summarizing the paragraph)
- Plot Summary
- Main Themes

Rules:
1. Extract only information supported by the paragraph.
2. Do not invent missing details. Write "Not specified".
3. Keep the summaries clear, concise, and easy to understand.
4. Return the result in a well-organized format.
"""),
('human',
"""
Extract information from this Paragraph:
{paragraph}
"""
)]
)

para = input("Give your Paragraph: ")

final_prompt = prompt.invoke(
    {"paragraph":para}
)

response = model.invoke(final_prompt)
print(response.text)
