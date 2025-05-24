import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from subProc.manualjson import manual_json_extraction

load_dotenv()


llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=1)  # type: ignore


associate_image_prompt_template = PromptTemplate.from_template(
    """
    - You are an AI assistant that manages product information for an inventory system.
    - Given a chat history, your job is to determine the specific product the user is referring to and associate it with an image path.
    - If the chat history provides enough context, identify the relevant product and attach the image path to it.
    - Products must have at least one image, so confirm the association or suggest the product is incomplete if no image is added.

    **Response Format SHOULD BE RAW VALID JSON:**
    {{
        "product_name": "<inferred name of the product from the chat history>",
        "image_path": "<provided image path>",
        "status": (1 if the image path was successfully associated with the product; 0 if the product could not be inferred or is missing)
    }}

    Chat History: "{chat_history}"
    Image Path: "{image_path}"
    You must respond strictly in JSON format. Do not include any other text or explanations.
    """
)

def associate_image_with_product_via_history(chat_history, image_path):
    while True:
        try:
            full_prompt = associate_image_prompt_template.format(
                chat_history=chat_history,
                image_path=image_path
            )
            
            response = llm.invoke(full_prompt)
            response_content = response.content.strip()  # type: ignore

            try:
                response_json = json.loads(response_content)
            except json.JSONDecodeError:
                print("Direct JSON parsing failed. Attempting manual extraction...")
                response_json = manual_json_extraction(response_content)

            required_keys = ["product_name", "image_path", "status"]
            if all(key in response_json for key in required_keys):
                print("RA DAROHAAA", response_json)
                return response_json
            else:
                raise ValueError("Invalid response structure: missing required fields.")

        except Exception as e:
            print(f"Error in associate_image_with_product_via_history: {e}")
            print("Retrying...")
