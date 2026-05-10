import json
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from pipeline.scraper import get_positions
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).parent.parent


class CVClassification(BaseModel):
    category: str
    position: str

async def classify_cv(cv_text: str) -> CVClassification:
    positions = await get_positions()

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
    )

    parser = PydanticOutputParser(pydantic_object=CVClassification)

    prompt = PromptTemplate(
        template="""
        Si expert na HR a kariérny poradca.

        Na základe tohto CV vyber PRESNE jednu kategóriu a jednu pozíciu z tohto zoznamu.
        Pozícia MUSÍ byť DOSLOVNE skopírovaná zo zoznamu, žiadne úpravy, žiadne pridávanie slov.

        ZOZNAM POZÍCIÍ:
        {positions}

        {format_instructions}

        CV:
        {cv_text}
        """,
        input_variables=["cv_text", "positions"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser

    result = chain.invoke({
        "cv_text": cv_text,
        "positions": json.dumps(positions, ensure_ascii=False, indent=2)
    })

    return result