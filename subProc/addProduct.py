import os

from openai import OpenAI
from dotenv import load_dotenv
import json 

load_dotenv()


from subProc.manualjson import manual_json_extraction

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

addProduct_prompt_template = PromptTemplate.from_template(
    """
        - You are an intelligent AI assistant for an e-commerce platform. Extract **only one product** from the input, even if the user mentions multiple products.
        - A product entry should contain: **NAME**, **PRICE**, **QUANTITY**, **DESCRIPTION**, and **CATEGORY**.
        - If the CATEGORY is "Clothing," also detect size and quantity variations (e.g., S, M, L sizes with their respective quantities).
        
        - If all required fields are present for a single product, return a status of 1 ( if its an 'state': 'updating_product', you can return status 1 ).
        - If any required fields are missing, return a status of 0.
        - If the input contains multiple distinct products, **regardless of whether it is for adding or updating**, return a status of 2.

        **Response Format MUST BE VALID JSON:**
        {{
            "text": "<original input text formatted as JSON>",
            "status": <0, 1, or 2>,
            "category": "<product category>",
            "variations": [
                {{"size": "<size>", "quantity": <quantity>}}
            ] if category == "Clothing" else []
        }}

        **Example 1 (Single Product):**
        Input: "I want to add a product: Nike T-shirt, Price: 30, Quantity: 200. Sizes available are S (50), M (100), L (50)."
        Output: {{
            "text": "Nike T-shirt, Price: 30, Quantity: 200",
            "status": 1,
            "category": "Clothing",
            "variations": [
                {{"size": "S", "quantity": 50}},
                {{"size": "M", "quantity": 100}},
                {{"size": "L", "quantity": 50}}
            ]
        }}

        **Example 2 (Multiple Products):**
        Input: "I have Nike shoes and Adidas shoes. Nike shoes are white with a quantity of 500 and price of 250. Adidas shoes have a quantity of 20 and price of 450."
        Output: {{
            "text": "Multiple products detected in input.",
            "status": 2
        }}

        **Example 3 (Non-Clothing Product):**
        Input: "I want to add a Samsung TV, Price: 5000, Quantity: 10."
        Output: {{
            "text": "Samsung TV, Price: 5000, Quantity: 10",
            "status": 1,
            "category": "Electronics",
            "variations": []
        }}

        input: "{question}"
        You must respond strictly in JSON format. Do not include any other text or explanations.
    """
)

llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=1) # type: ignore

def makeSureitsProduct(question):
    
    while True:
        try:
            full_prompt = addProduct_prompt_template.format(question=question)
            response = llm.invoke(full_prompt)

            response_content = response.content.strip()  # type: ignore

            try:
                response_json = json.loads(response_content)
            except json.JSONDecodeError:
                print("Direct JSON parsing failed. Attempting manual extraction...")
                response_json = manual_json_extraction(response_content)

            # Ensure the response is a valid dictionary
            if isinstance(response_json, dict):
                return response_json
            else:
                raise ValueError("The extracted response is not a valid JSON dictionary.")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error: {e}. makeSureitsProduct Retrying...")