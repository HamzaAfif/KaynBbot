import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from subProc.manualjson import manual_json_extraction
load_dotenv()

llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=1) # type: ignore

product_details_prompt_template = PromptTemplate.from_template(
    """
    You are an intelligent assistant tasked with extracting product details from a user's input.
    You are provided with a list of existing product names as context. Determine if the product mentioned by the user already exists or if it is a new entry.
    Based on the user's input and the context provided, return the following fields in a valid JSON format:

    **Required Response Format:**
    **Response Format MUST BE VALID JSON:**
    {{
        "product_name": "<product name>",
        "price": <price>,  # numerical value
        "quantity": <quantity>,  # integer value
        "description": "<product description>",
        "category": "<product category>",
        "variations": [
            {{
                "variation_name": "<variation name (e.g., size, color)>",
                "value": "<variation value (e.g., 'M', 'Red')>",
                "price": <variation price>,  # corrected field name
                "quantity": <quantity for this variation>
            }}
        ],
        "status": "<updating or adding>",
        "image_path": "["<image path 1>", "<image path 2>", ...] (e.g., image path if provided)"
    }}

    Notes:
    - If the product name matches or is similar to an existing product from the provided context, set the **status** to "updating".
    - If the product name is new and not found in the existing products list, set the **status** to "adding".
    - If the user's input contains different sizes, colors, or other variations, include them in the `variations` field.
    - If no variations are mentioned, return an empty list for `variations`.
    - If the user's input does not contain any of the required fields, return the missing fields as null. For example:
    {{
        "product_name": null,
        "price": null,
        "quantity": null,
        "description": null,
        "category": null,
        "variations": [],
        "status": "adding"
    }}

    **Store Context (Existing Products):**
    {existing_products}
    
    **Unassociated Image Path:**
    "{image_path}"

    Input: "{question}"
    You must respond strictly in JSON format. Do not include any other text or explanations.
    """
)

def fetch_product_details_from_ai(user_input, existing_products, unassociated_image_path=None):
    existing_products_list = [p["product_name"] for p in existing_products if "product_name" in p]
    
    full_prompt = product_details_prompt_template.format(
        question=user_input,
        existing_products=existing_products_list,
        image_path=unassociated_image_path or ""
    )
    
    while True:
        try:
            response = llm.invoke(full_prompt)
            response_content = response.content.strip()  # type: ignore

            try:
                response_json = json.loads(response_content)
            except json.JSONDecodeError:
                print("Direct JSON parsing failed. Attempting manual extraction...")
                response_json = manual_json_extraction(response_content)

            required_keys = ["product_name", "price", "quantity", "description", "category", "variations", "image_path"]
            for key in required_keys:
                if key not in response_json:
                    response_json[key] = None if key != "variations" else []

            if all(key in response_json for key in required_keys):
                return response_json
            else:
                print("Missing one or more product fields in JSON response.")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error: {e}. Response content: {response_content}")
            print("Retrying...")