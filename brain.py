import os
from langChain import generate_sql_query
from classes.user import User
from classes.session import Session
from openai import OpenAI
from dotenv import load_dotenv
import json 


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



    
def run_conversation():
    
    user = User(115, 'English')
    session = Session(user)
    
    system_message = {
        "role": "system",
        "content": """
        You are an intelligent assistant for an e-commerce platform called EasyFind. Your name is Easy. Your primary goal is to assist users in managing their product listings, inventory, and store preferences through natural, context-aware conversations.

        **Key Responsibilities:**
        - **Maintain Context:** Keep track of ongoing conversations, remembering important details like product names, quantities, prices, and user preferences.
        - **User Requests:** Efficiently handle requests for product listings, inventory updates, and store preferences while maintaining a natural flow in conversation.
        - **Seamless Transitions:** If a user shifts topics, ensure you remember what they were previously working on so they can easily return to it.
        - **Language Preferences:** Respond in the user's preferred language if they request a language change during the session.
        - **Clarifying Questions:** Ask clarifying questions when necessary to gather information without being repetitive or redundant.
        - **Action Confirmation:** Confirm actions when appropriate, for example, "Would you like to save this product?"

        **Response Format RAW JSON -IMPORTANT-:**
        - Return all responses in PURE RAW IN JSON format with the following structure:
            - **text:** The assistant's reply to the user.
            - **status:** Set this to `1` ONLY when you have gathered ALL necessary information and got a positive confirmation to save. For all other responses, set `status` to `0`.
            - **state:** The current state of the conversation. It can be `general_chat`, `adding_store`, `adding_product`, or any other relevant states.
        """
    }

    
    session.add_chat("system", system_message["content"])

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
            
            assistant_reply_json = json.loads(assistant_reply)  # type: ignore
            session.add_chat("assistant", assistant_reply_json["text"])
            
            session.set_state(assistant_reply_json.get("state", session.get_state()))
            print("Easy:", assistant_reply_json)

            current_state = session.get_state()
            
            if current_state == 'adding_store':
                if assistant_reply_json["status"] == 1 or '1':
                    print("\n**Moving to add SQL... adding_store** \n")
                else :
                    pass
            
            if current_state == 'adding_product':
                if assistant_reply_json["status"] == 1:
                    print("\n**Moving to add SQL... adding_product** \n")
                else :
                    pass        
            
            # if assistant_reply_json["status"] == 1:
                #print("\n**Moving to add SQL...** \n")
                
                #confirmation_details = assistant_reply_json["text"]
                #print("Confirmation Details:", confirmation_details)
                
                #print(generate_sql_query(confirmation_details))
                #print("\n")
                
        except (json.JSONDecodeError, KeyError) as e:
            
            print(f"Error: Unable to parse assistant's reply as JSON. Details: {e} \n")
            print(assistant_reply)
         
      
if __name__ == "__main__":
    run_conversation()  
