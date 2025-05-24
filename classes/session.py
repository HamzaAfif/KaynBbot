from classes.store import Store
from classes.product import Product
from classes.user import User
import logging
logging.basicConfig(filename='ai_debug.log', level=logging.INFO)

class Session:
    def __init__(self, user):
        self.user = user  # Instance of User class
        self.state = 'general_chat'  # Initial state
        self.chat_history = []  
        self.store_info = None  
        self.product_info = None  
        self.is_locked = False
        self.unassociated_image_paths = [] 

    def add_unassociated_image_path(self, image_path):
        self.unassociated_image_paths.append(image_path)

    def get_unassociated_image_paths(self):
        return self.unassociated_image_paths

    def clear_unassociated_image_paths(self):
        self.unassociated_image_paths = []
        
    def lock(self):
        print("lock")
        self.is_locked = True

    def unlock(self):
        print("unlock")
        self.is_locked = False

    def is_session_locked(self):
        return self.is_locked
    
    def add_chat(self, role, content):
        
        logging.info(f"role: {role}, content: {content}")
        
        self.chat_history.append({"role": role, "content": content})
    
    def set_state(self, new_state):

        self.state = new_state
    
    def get_state(self):

        return self.state
    
    def check_store_exists(self):

        return self.user.store is not None

    def start_adding_store(self):

        self.set_state('adding_store')
        self.store_info = {}  # Initialize an empty dictionary to store info

    def save_store_info(self):

        if not self.store_info:
            return "No store info to save."
        
        store_name = self.store_info.get("store_name")
        store_location = self.store_info.get("store_location")
        
        if not store_name or not store_location:
            return "Store details are incomplete."
        
        self.user.add_store(store_name, store_location)
        self.store_info = None  # Clear the store info
        self.set_state('general_chat')  # Return to general state
        return f"Store '{store_name}' created successfully!"
    
    def add_image_to_product(self, product_name, image_path):
        
        return self.user.add_image_to_product(product_name, image_path)