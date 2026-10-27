import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
#for schema
from pydantic import BaseModel
#for parser
from typing import List,Optional
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    max_tokens=200
)

#creating schema
class Movie(BaseModel):
    title: str 
    release_year : Optional[int]
    genre: List[str]
    director: Optional[str]
    cast: List[str]
    rating: Optional[float]
    summary: str

#creating parser
parser = PydanticOutputParser(pydantic_object=Movie)

prompt = ChatPromptTemplate.from_messages(
[("system",
"""
You are a movie information extraction assistant.

Analyze the given movie paragraph and extract useful information.

{format_instructions}
"""),
('human',
"""
{paragraph}
"""
)]
)

para = input("Give your Paragraph: ")

final_prompt = prompt.invoke(
    {
        "paragraph":para,
        "format_instructions": parser.get_format_instructions()
    }
)

response = model.invoke(final_prompt)
print(response.text)
