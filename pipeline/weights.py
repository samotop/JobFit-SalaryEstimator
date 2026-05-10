import json
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
WEIGHTS_DATA = BASE_DIR / "data" / "weights.json"

FACTORS = [
    "years_of_experience",
    "education_level",
    "role_seniority",
    "skillset_relevance",
    "certifications",
    "language_skills",
    "project_scope",
    "personality_traits"
]

class SectorWeights(BaseModel):
    years_of_experience: int
    education_level: int
    role_seniority: int
    skillset_relevance: int
    certifications: int
    language_skills: int
    project_scope: int
    personality_traits: int

def load_weights() -> dict:
    try:
        with open(WEIGHTS_DATA, "r", encoding="utf-8") as f:
            content = f.read()
            if not content:
                return {}
            return json.loads(content)
    except FileNotFoundError:
        return {}

def save_weights(weights: dict):
    with open(WEIGHTS_DATA, "w", encoding="utf-8") as f:
        json.dump(weights, f, ensure_ascii=False, indent=2)

async def get_weights(category: str, position: str) -> SectorWeights:
    weights = load_weights()
    key = f"{category}.{position}"

    if key in weights:
        return SectorWeights(**weights[key])

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    parser = PydanticOutputParser(pydantic_object=SectorWeights)

    prompt = PromptTemplate(
        template="""
Si expert na HR.

Pre pozíciu "{position}" v kategórii "{category}" ohodnoť dôležitosť 
každého faktoru na škále 1-10.

Faktory:
- years_of_experience: roky praxe
- education_level: úroveň vzdelania
- role_seniority: seniorita predošlých rolí
- skillset_relevance: relevantnosť skillsov
- certifications: certifikáty
- language_skills: jazykové znalosti
- project_scope: veľkosť projektov
- personality_traits: osobnostné rysy

{format_instructions}
        """,
        input_variables=["category", "position"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser
    result = chain.invoke({"category": category, "position": position})

    weights[key] = result.model_dump()
    save_weights(weights)

    return result