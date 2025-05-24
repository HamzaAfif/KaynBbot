import os

from openai import OpenAI
from dotenv import load_dotenv
import json 

load_dotenv()



from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

json_prompt_template = PromptTemplate.from_template(
     """
        You are an AI assistant, and your task is to convert the input into a valid JSON format. 
        The JSON must include the following structure:

        {{
            "text": "<original input text>",
            "state": "<current state ( general_chat, adding_store, adding_product, updating_product) >"
        }}

        Please respond only with the JSON object and no other text.

        Input: "{question}"
        You must respond strictly in JSON format. Do not include any other text or explanations.
    """
)
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=1) # type: ignore

def makeSureitsJson(question):

    full_prompt = json_prompt_template.format(question=question)

    while True:
        try:
            response = llm.invoke(full_prompt)
            response_content = response.content.strip()  # type: ignore

            # Attempt to load JSON directly first
            try:
                response_json = json.loads(response_content)
                if "text" in response_json and "state" in response_json:
                    return response_json
                else:
                    raise ValueError("Missing expected keys in JSON response.")

            except json.JSONDecodeError:
                print("Direct JSON parsing failed. Attempting manual extraction...")

                start_index = response_content.find('{')
                end_index = response_content.rfind('}')

                if start_index != -1 and end_index != -1 and start_index < end_index:
                    json_string = response_content[start_index:end_index + 1]

                    try:
                        response_json = json.loads(json_string)
                        if "text" in response_json and "state" in response_json:
                            return response_json
                        else:
                            raise ValueError("Extracted JSON is missing expected keys.")
                    except json.JSONDecodeError as e:
                        print(f"Manual JSON extraction failed: {e}")

                print("Failed to parse JSON Mnually. Returning default response.")
                

        except Exception as e:
            print(json_string)
            print(f"Error in makeSureitsJson: {e}. Retrying...")