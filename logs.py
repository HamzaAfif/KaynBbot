import logging

logging.basicConfig(filename='ai_debug.log', level=logging.INFO)

def log_interaction(user_input, assistant_reply):
    logging.info(f"User: {user_input}")
    logging.info(f"Assistant: {assistant_reply}")


#log_interaction("Show me products", "Here are the products.")