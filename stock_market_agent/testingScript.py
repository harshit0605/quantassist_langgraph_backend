from typing import List

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
class Joke(BaseModel):
    setup: str = Field(description="question to set up a joke")
    punchline: str = Field(description="answer to resolve the joke")

    # You can add custom validation logic easily with Pydantic.
    # @validator("setup")
    # def question_ends_with_question_mark(cls, field):
    #     if field[-1] != "?":
    #         raise ValueError("Badly formed question!")
    #     return field
    
def main():
    load_dotenv()
    joke_query = "Tell me a joke."
    model = ChatOpenAI(temperature=0)

    parser = PydanticOutputParser(pydantic_object=Joke)
    prompt = PromptTemplate(
        template="Answer the user query.\n\n{query}\n",
        input_variables=["query"],
        # partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model.with_structured_output(Joke) #| parser

    response = chain.invoke({"query": joke_query})
    print
    if isinstance(response, Joke):
        print(response.setup, response.punchline)
    else:
        print("Unexpected response format:", response)
    # print(resp.setup, resp.punchline)

if __name__ == "__main__":
    main()