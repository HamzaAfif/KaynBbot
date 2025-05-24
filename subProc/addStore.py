import os

from openai import OpenAI
from dotenv import load_dotenv
import json 
from subProc.manualjson import manual_json_extraction


load_dotenv()



from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

addStore_prompt_template = PromptTemplate.from_template(
    r"""
        - You are an AI assistant, and your task is to process input text to create a store record in JSON format.
        - A store record must include a NAME and LOCATION.
        
        - If both NAME and LOCATION are present, set **"status"** to 1.
        - If either NAME or LOCATION is missing, set **"status"** to 0.

        **Response Format MUST BE JSON**:
        {{
            "text": "<original input text>",
            "status": <0 or 1>
        }}

        **Example:**
        Input: "Create a store named 'Bistro Cafe' in New York City."
        Output: {{
            "text": "Create a store named 'Bistro Cafe' in New York City.",
            "status": 1
        }}

        input: "{question}"
        You must respond strictly in JSON format. Do not include any other text or explanations.
    """
)


llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=1) # type: ignore

def makeSureitsStore(question):
    while True:
        try:
            full_prompt = addStore_prompt_template.format(question=question)
            response = llm.invoke(full_prompt)

            response_content = response.content.strip()  # type: ignore

            try:
                response_json = json.loads(response_content)
            except json.JSONDecodeError:
                print("Direct JSON parsing failed. Attempting manual extraction...")
                response_json = manual_json_extraction(response_content)

            if "text" in response_json and "status" in response_json:
                return response_json
            else:
                raise ValueError("Missing 'text' or 'status' in JSON response.")

        except Exception as e:
            print(f"Error in makeSureitsStore: {e}. Response content: {response_content}")
            print("Retrying...")
