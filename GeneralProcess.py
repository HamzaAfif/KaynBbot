import os
from langchain_core.prompts import PromptTemplate
from openai import OpenAI
from dotenv import load_dotenv
from classes.user import User
from classes.session import Session
from subProc.jsonProc import makeSureitsJson
from subProc.addStore import makeSureitsStore
from subProc.addProduct import makeSureitsProduct
from langChain import generate_sql_query

import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



system_message_template = PromptTemplate.from_template(
    """
    You are an intelligent assistant for an e-commerce platform called EasyFind. Your name is Easy. 
    Your primary goal is to assist users in managing their product listings, inventory, and store preferences through natural, context-aware conversations.

    **Important Rules:**
    - **Store needs to be created first:** YOU SHALL NOT CONTINUE UNTIL THE USER HAS AT LEAST ONE STORE.

    **Key Responsibilities:**
    - **Maintain Context:** Keep track of ongoing conversations, remembering important details like product names, quantities, prices, and user preferences.
    - **User Requests:** Efficiently handle requests for product listings, inventory updates, and store preferences while maintaining a natural flow in conversation.
    - **Seamless Transitions:** If a user shifts topics, ensure you remember what they were previously working on so they can easily return to it.
    - **Language Preferences:** Respond in the user's preferred language if they request a language change during the session.
    - **Clarifying Questions:** Ask clarifying questions when necessary to gather information without being repetitive or redundant.
    - **Action Confirmation:** Confirm actions when appropriate, for example, "Would you like to save this product?"

    **Structure of Classes:**
    - **Product:** A product should always have: NAME, PRICE, Quantity, Type, and Description (you should generate Type and Description by yourself).
    - **Store:** A store should always have: Name, Location.
    - **User:** The user is the owner and has as its ID {user_id} (UNCHANGEABLE, CONFIDENTIAL), and preferred language {preferred_language}.

    """
)


def run_conversation():
    
    user = User(115, 'English')
    session = Session(user)
    
    # Generate the system message based on user context
    system_message = system_message_template.format(
        user_id=user.user_id, 
        preferred_language=user.preferred_language
    )
    
    
    session.add_chat("system", system_message)

    print("Welcome to EasyFind AI Assistant! (Type 'exit' to end the conversation)\n")

    while True:
        user_input = input("User: ")

        if user_input.lower() == 'exit':
            print("Ending the conversation. Goodbye!")
            break

        session.add_chat("user", user_input)

        response = client.chat.completions.create(
            messages=[{"role": msg["role"], "content": msg["content"]} for msg in session.chat_history], 
            model="gpt-4o-mini",
            temperature=1,  # Adjust the temperature for response variability
            max_tokens=2048,    # Limit response length
        )
        
        #assistant_reply = response
        
        assistant_reply = response.choices[0].message.content
        
        try:

            assistant_reply_json = makeSureitsJson(assistant_reply) # type: ignore
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
                    confirmation_details = assistant_reply_json["text"]
                    print(generate_sql_query(confirmation_details))
                    

            
            if current_state == 'adding_product':
                print(f"\nchecking...  |adding_product| \n")
                checker = makeSureitsProduct(assistant_reply_json)
                
                print(f'\n status : {checker["status"]}\n')

                if int(checker["status"]) == 1:
                    
                    print("\n**Moving to add SQL... adding_product** \n")
                    confirmation_details = assistant_reply_json["text"]
                    print(generate_sql_query(confirmation_details))
                    
                
        except (json.JSONDecodeError, KeyError) as e:
            
            print(f"Error: Unable to parse assistant's reply as JSON. Details: {e} \n")
            makeSureitsJson(assistant_reply)
            print(assistant_reply)
         
      
if __name__ == "__main__":
    run_conversation()  