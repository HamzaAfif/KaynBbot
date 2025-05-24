import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from subProc.manualjson import manual_json_extraction
load_dotenv()

llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=1) # type: ignore

store_details_prompt_template = PromptTemplate.from_template(
    """
    You are an intelligent assistant tasked with extracting store details from a user's input. 
    Given the user's message, return the following fields in a valid JSON format:

    **Required Response Format:**
    {{
        "store_name": "<store name>",
        "store_location": "<store location>"
    }}

    If the user's input does not contain a store name or store location, respond with:
    {{
        "store_name": null,
        "store_location": null
    }}

    Input: "{question}"
    You must respond strictly in JSON format. Do not include any other text or explanations.
    """
)

def fetch_store_details_from_ai(user_input):
    full_prompt = store_details_prompt_template.format(question=user_input)
    
    while True:
        try:
            response = llm.invoke(full_prompt)
            response_content = response.content.strip()  # type: ignore 


            try:
                response_json = json.loads(response_content)
            except json.JSONDecodeError:
                print("Direct JSON parsing failed. Attempting manual extraction...")
                response_json = manual_json_extraction(response_content)

            if "store_name" in response_json and "store_location" in response_json:
                return response_json
            else:
                raise ValueError("Missing 'store_name' or 'store_location' in JSON response.")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error: {e}. Retrying...")


