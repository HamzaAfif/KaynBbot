import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from subProc.manualjson import manual_json_extraction
import os

llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=1)  # type: ignore

# New prompt template for image and product association
image_product_manager_prompt = PromptTemplate.from_template(
    """
    You are a smart assistant that handles product details and image association for an e-commerce platform.
    You need to manage both unassociated images and incomplete product details. Here’s your task:

    **Context:**
    - There are unassociated images: {unassociated_images}
    - Incomplete product details: {incomplete_product_details}

    **Your Responsibilities:**
    - If product details are missing but images are present, ask the user for the product details (name, price, quantity, etc.).
    - If product details are provided but no image has been associated yet, wait for the user to upload the image.
    - If both product details and images are available, finalize the product entry and return a confirmation message.
    - If the product name matches an existing product, set the status to "updating". Otherwise, set it to "adding".

    **Response Format MUST BE VALID JSON:**
    {{
        "status": "<adding or updating>",
        "product_name": "<product name>",
        "price": <price>,
        "quantity": <quantity>,
        "description": "<product description>",
        "category": "<product category>",
        "variations": [
            {{
                "variation_name": "<variation name>",
                "value": "<variation value>",
                "price": <variation price>,
                "quantity": <variation quantity>
            }}
        ],
        "image_paths": {unassociated_images}
    }}

    Input: "{question}"
    You must respond strictly in JSON format. Do not include any other text or explanations.
    """
)

def manage_image_product_association(question, unassociated_images, incomplete_product_details=None):
    # Prepare the context for the prompt
    context = {
        "unassociated_images": unassociated_images,
        "incomplete_product_details": incomplete_product_details or {}
    }

    full_prompt = image_product_manager_prompt.format(
        question=question,
        unassociated_images=unassociated_images,
        incomplete_product_details=context["incomplete_product_details"]
    )

    while True:
        try:
            response = llm.invoke(full_prompt)
            response_content = response.content.strip()

            try:
                response_json = json.loads(response_content)
            except json.JSONDecodeError:
                print("Direct JSON parsing failed. Attempting manual extraction...")
                response_json = manual_json_extraction(response_content)

            return response_json

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error: {e}. Retrying...")
