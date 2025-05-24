from telegram import Update, Bot, File, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters,CallbackContext, CallbackQueryHandler
from telegram.constants import ParseMode
import json

import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))




import os
from langchain_core.prompts import PromptTemplate
from openai import OpenAI
from dotenv import load_dotenv
from classes.user import User
from classes.session import Session
from classes.product import Product
from classes.store import Store
from subProc.jsonProc import makeSureitsJson
from subProc.addStore import makeSureitsStore
from subProc.addProduct import makeSureitsProduct
from langChain import generate_sql_query
from subProc.getNameLocation import fetch_store_details_from_ai
from subProc.getProductDetails import fetch_product_details_from_ai
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



user_sessions = {}

system_message_template = PromptTemplate.from_template(
    """
    You are an intelligent assistant for an e-commerce platform called KaynBot. Your name is Kayn. 
    Your primary goal is to assist users in managing their product listings, inventory, and store preferences through natural, context-aware conversations.

    **Important Rules:**
    - **Store needs to be created first:** YOU SHALL NOT CONTINUE UNTIL THE USER HAS AT LEAST ONE STORE.
    - **If multiple products are mentioned in a single message, stop and ask the user to clarify or add one product at a time.**
    - **System Messages:** If the message was from the system, do not treat it as an empty user input. Instead, respond to the user based on the instructions or context provided by the system message.

    **Key Responsibilities:**
    - **Maintain Context:** Keep track of ongoing conversations, remembering important details like product names, quantities, prices, and user preferences.
    - **User Requests:** Efficiently handle requests for product listings, inventory updates, and store preferences while maintaining a natural flow in conversation.
    - **Seamless Transitions:** If a user shifts topics, ensure you remember what they were previously working on so they can easily return to it.
    - **Language Preferences:** Respond in the user's preferred language if they request a language change during the session.
    - **Clarifying Questions:** Ask clarifying questions when necessary to gather information without being repetitive or redundant.
    - **Action Confirmation:** Confirm actions when appropriate, for example, "Would you like to save this product?"

    **Structure of Classes:**
    - **Product:** A product should always have: NAME, PRICE, Quantity, Images (store the image path temporarily if the image is uploaded before the product details), CATEGORY (Clothing...), and Description (you should generate CATEGORY and Description by yourself and show them to user), if the product category is in cothes ask for variations (e.g., S, M, L sizes with their respective quantities).
    - **Store:** A store should always have: Name and a descriptive location (e.g., City or Area Name), when added and store succefully added ask about live GPS coordinates from the user.
    - **User:** The user is the owner with the following data: {data}. If no data is available, the user is new.
    
    from time to time reply with some emojies
    """
)


def get_or_create_session(user_id):
    if user_id not in user_sessions:
        # Load user data from JSON
        user_data = load_user_data_from_json(user_id)
        
        if user_data:
            # Create the user instance
            user = User(user_data['user_id'], user_data['preferred_language'])
            
            if 'store' in user_data:
                store_data = user_data['store']
                user.store = Store(
                    store_name=store_data.get('store_name', 'Unknown'),
                    store_location=store_data.get('store_location', 'Unknown location')
                )
                
                # Load and assign products if they exist
                products = store_data.get('products', [])
                for product_data in products:
                    product = Product(
                        product_name=product_data.get('product_name', 'Unnamed Product'),
                        price=product_data.get('price', 0),
                        quantity=product_data.get('quantity', 0),
                        description=product_data.get('description', ''),
                        image_paths=product_data.get('image_paths', []),
                        variations=product_data.get('variations', [])
                    )
                    user.store.products.append(product)  # Add product to store's product list

                # Debugging: Print store and product details to confirm loading
                print(f"Loaded store: {user.store.store_name}")
                for p in user.store.products:
                    print(f"Loaded product: {p.product_name}, Price: {p.price}, Quantity: {p.quantity}")

            # Context message based on loaded store and products
            store_name = user.store.store_name if user.store else "No store"
            latitude = user.store.store_location.get('latitude', 'Unknown') if isinstance(user.store.store_location, dict) else 'Unknown latitude'
            longitude = user.store.store_location.get('longitude', 'Unknown') if isinstance(user.store.store_location, dict) else 'Unknown longitude'
            product_details = "\n".join(
                [
                    f"Product Name: {p.product_name}, "
                    f"Price: {p.price}, "
                    f"Quantity: {p.quantity}, "
                    f"Description: {p.description},"
                    f"Images: {True if p.image_paths else False}, "
                    f"Variations: {p.variations}"
                    for p in user.store.products
                ]
            )
            
            context_message = (
                f"User {user_id} has an existing store: {store_name} "
                f"located at latitude {latitude}, longitude {longitude}. "
                f"Products:\n{product_details}"
            )
        else:
            # Create a new user if no existing data is found
            user = User(user_id, 'English')
            context_message = "No store data available. The user is new."
        
        # Create a session with the user object
        session = Session(user)

        # Add the initial system message to the session
        system_message = system_message_template.format(
            user_id=user.user_id, 
            preferred_language=user.preferred_language,
            data=context_message
        )
        session.add_chat("system", system_message)

        # Save the session in the global user_sessions dictionary
        user_sessions[user_id] = session

    return user_sessions[user_id]




def load_user_data_from_json(user_id):
    file_path = f"data/users/{user_id}.json"
    
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            user_data = json.load(json_file)
            return user_data  # Return JSON data as a dictionary
    else:
        print(f"No data found for user {user_id}. Starting with empty data.")
        return None

    
    
def run_conversation(user_message, user_id, system_message=None):
    
    session = get_or_create_session(user_id)  # Get the session for this user
    
    
    
    if system_message:
        session.add_chat("system", system_message)
        
        
    session.add_chat("user", user_message)
    
    messages = [{"role": "system", "content": system_message}] if system_message else []
    messages += [{"role": msg["role"], "content": msg["content"]} for msg in session.chat_history]

    response = client.chat.completions.create(
        messages= messages, 
        model="gpt-4o-mini",
        temperature=1,  # Adjust the temperature for response variability
        max_tokens=2048,    # Limit response length
    )
    
    assistant_reply = response.choices[0].message.content
    
    try:
        assistant_reply_json = makeSureitsJson(assistant_reply)  # Parse the response as JSON if possible
        session.add_chat("assistant", assistant_reply_json["text"])
        
        session.set_state(assistant_reply_json.get("state", session.get_state()))
        print("Easy:", assistant_reply_json)

        current_state = session.get_state()

        if current_state == 'adding_store':  
            print(f"\nchecking...  |adding_store| \n")
            checker = makeSureitsStore(assistant_reply_json)
            
            print(f'\n status : {checker["status"]}\n')
            
            if int(checker["status"]) == 1:
                print("\n**Moving to add SQL... adding_store** \n")
                store_details = fetch_store_details_from_ai(assistant_reply)
                
                print("HAHOMAAAA", store_details)
                
                store_name = store_details["store_name"]
                store_location = store_details["store_location"]
                
                #make sure the AI checks the json file before moving this way nkono sure he added the store
                #it just got me the message added succesfully but no store was done ola likan gha message with no generate sql query action
                
                print("HAHOMAAAA 2222 ", store_name, store_location)
                
                session.user.add_store(store_name, store_location)
                
                confirmation_details = assistant_reply_json["text"]
                print(generate_sql_query(confirmation_details))

        if current_state == 'adding_product' or current_state == 'updating_product':
            print(f"\nchecking...  |adding_product| \n")
            checker = makeSureitsProduct(assistant_reply_json)
            
            print(f'\n status : {checker["status"]}\n')

            if int(checker["status"]) == 1:
                print("\n**Moving to add SQL... adding_product** \n")
                
                existing_products = session.user.get_all_products()
                unassociated_image_paths = session.get_unassociated_image_paths()
                print("Existing Products: ", existing_products)
        
                product_details = fetch_product_details_from_ai(assistant_reply, existing_products, unassociated_image_paths)
                
                print("Product Details: ", product_details)
                 
                product_id = product_details.get("product_id")  # Use product_id if available
                product_name = product_details["product_name"]
                price = product_details["price"]
                quantity = product_details["quantity"]
                description = product_details["description"]
                category = product_details.get("category", "")
                variations = product_details.get("variations", [])
                
                
                if product_id:
                    existing_product = session.user.get_product_by_id(product_id)
                elif product_name:
                    existing_product = session.user.get_product_by_name(product_name)
                else:
                    existing_product = None  
                    
                if existing_product:
                    print(f"Updating existing product: {product_name}")
                    session.user.update_product_in_store(
                        product_id=product_id,  # Use product_id if available, else None
                        product_name=product_name, 
                        new_quantity=quantity, 
                        new_price=price, 
                        new_description=description,
                        new_variations=variations
                    )
                    if unassociated_image_paths:
                        for image_path in unassociated_image_paths:
                            session.user.add_image_to_product(product_name, image_path)
                        session.clear_unassociated_image_paths()
                        print(f"All images associated with existing product '{product_name}'.")
                else:
                    print(f"Adding new product: {product_name}")
                    session.user.add_product_to_store(product_name, price, quantity, description, category, variations)
                    if unassociated_image_paths:
                        for image_path in unassociated_image_paths:
                            session.user.add_image_to_product(product_name, image_path)
                        session.clear_unassociated_image_paths()
                        print(f"All images associated with new product '{product_name}'.")

                confirmation_details = assistant_reply_json["text"]
                print(generate_sql_query(confirmation_details))
                
            elif int(checker["status"]) == 2: #detected multiple product
                print("\n**Multiple products detected. Asking AI to clarify...**\n")

                system_message = (
                    "The input provided seems to contain multiple distinct products. "
                    "Please guide the user to add products one by one for better accuracy. "
                    "Ask the user to provide details for the first product, then proceed with others."
                )

                assistant_reply = run_conversation(
                    user_message=system_message,  
                    user_id=user_id,
                    system_message=system_message
                )

                return assistant_reply
                
            
        return assistant_reply_json["text"]
                
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error: Unable to parse assistant's reply as JSON. Details: {e} \n")
        makeSureitsJson(assistant_reply)
        print(assistant_reply)

        return assistant_reply  # Return raw reply if parsing fails  










from telegram import Update
from telegram.ext import ContextTypes

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = str(update.message.text).lower()
    user_id = update.message.from_user.id  # Get the Telegram user ID

    print(f"User {user_id} sent: {user_message}")
    
    # Run conversation and pass the user message and user ID
    assistant_reply = run_conversation(user_message, user_id)
    
    # Reply with the assistant's response
    await update.message.reply_text(assistant_reply)



        