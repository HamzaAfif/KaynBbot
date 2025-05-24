import json
import os
from classes.store import Store
from classes.product import Product
import uuid
import os

class User:
    def __init__(self, user_id, preferred_language):
        self.user_id = user_id
        self.preferred_language = preferred_language
        self.store = None  
        self.products = []  
        self.incomplete_product = None  
    
    
    def add_store(self, store_name, store_location):

        self.store = Store(store_name, store_location)
        self.save_to_json()  

    def add_product_to_store(self, product_name, price, quantity, description, category="", variations=None):
        if self.store is None:
            return "Add a store first."
        
        # Create the Product instance (it will have a unique product_id)
        product = Product(product_name, price, quantity, description, category, variations=variations)
        self.store.products.append(product)
        self.save_to_json()
        
        return f"Product '{product_name}' with ID '{product.product_id}' added to store '{self.store.store_name}'."



    def save_to_json(self):

        user_data = {
            "user_id": self.user_id,
            "preferred_language": self.preferred_language,
            "store": {
                "store_name": self.store.store_name if self.store else None,
                "store_location": self.store.store_location if self.store else None,
                "products": [product.to_dict() for product in self.store.products] if self.store else []
            },
            "incomplete_product": self.incomplete_product.to_dict() if self.incomplete_product else None
        }
        
        file_path = f"data/users/{self.user_id}.json"
        with open(file_path, "w") as json_file:
            json.dump(user_data, json_file, indent=4)
        print(f"User data saved to {file_path}")
    
    def load_from_json(self):

        file_path = f"data/users/{self.user_id}.json"
        
        if os.path.exists(file_path):
            with open(file_path, "r") as json_file:
                data = json.load(json_file)
                self.user_id = data["user_id"]
                self.preferred_language = data["preferred_language"]
                

                if data["store"]:
                    self.store = Store(data["store"]["store_name"], data["store"]["store_location"])
                    self.store.products = [Product.from_dict(p) for p in data["store"]["products"]] # type: ignore

                if data["incomplete_product"]:
                    self.incomplete_product = Product.from_dict(data["incomplete_product"]) # type: ignore
                
                print(f"User data loaded from {file_path}")
        else:
            print(f"No existing data found for user {self.user_id}.")
        
    def update_product_in_store(self, product_id=None, product_name=None, new_quantity=None, new_price=None, new_description=None, new_variations=None):
        """Update a product's details using either product_id or product_name."""
        
        if product_id:
            product = self.get_product_by_id(product_id)
        elif product_name:
            product = self.get_product_by_name(product_name)
        else:
            print("Error: Must provide either product_id or product_name.")
            return "Product update failed: No valid identifier provided."
        
        if product:
            if new_quantity is not None:
                product.quantity = new_quantity
            if new_price is not None:
                product.price = new_price
            if new_description is not None:
                product.description = new_description

            if new_variations:
                existing_variations = {f"{v['variation_name'].lower()}:{v['value'].lower()}": v for v in product.variations}

                for new_var in new_variations:
                    var_key = f"{new_var['variation_name'].lower()}:{new_var['value'].lower()}"

                    if var_key in existing_variations:
                        existing_variations[var_key]['quantity'] = new_var.get('quantity', existing_variations[var_key]['quantity'])
                        existing_variations[var_key]['price'] = new_var.get('price', existing_variations[var_key].get('price'))
                    else:
                        existing_variations[var_key] = new_var

                product.variations = list(existing_variations.values())

            self.save_to_json()
            return f"Product '{product.product_name}' with ID '{product.product_id}' has been updated."
        
        return "Product not found."




    
    def get_product_by_name(self, product_name):
        if self.store is None:
            self.load_from_json()  # Ensure we load data from JSON if it's not in memory
        if self.store is None:
            return None  # If there's still no store, return None
        for product in self.store.products:
            # Perform case-insensitive matching
            if product.product_name and product.product_name.lower() == product_name.lower():
                return product  # Return the product object if found
        return None  # Return None if no matching product is found


    def get_product_by_id(self, product_id):
        """Retrieve a product by its unique ID."""
        if self.store is None:
            self.load_from_json()
        if self.store:
            for product in self.store.products:
                if product.product_id == product_id:
                    return product
        return None
    
    def add_image_to_product(self, product_name, image_path):
        # Ensure store and products are loaded
        if self.store is None:
            self.load_from_json()

        for product in self.store.products:
            if product.product_name == product_name:
                # Use product_id to create a unique directory for images
                product_dir = f"data/pictures/products/user_{self.user_id}/{product.product_id}"
                os.makedirs(product_dir, exist_ok=True)

                # Generate a unique filename for each image
                unique_filename = f"{uuid.uuid4()}.jpg"
                unique_image_path = os.path.join(product_dir, unique_filename)

                # Save the image to the unique path
                os.rename(image_path, unique_image_path)  # Move the file to the new path

                # Add the new image path to the product's image_paths
                product.image_paths.append(unique_image_path)
                self.save_to_json()  # Save the updated data to JSON
                print(f"Image path added to product '{product_name}'.")

                return f"Image added to product '{product_name}' at {unique_image_path}."

        return f"Product '{product_name}' not found."
    
    
    def get_all_products(self):

        if self.store is None:
            self.load_from_json()  # Ensure we load data from JSON if the store is not in memory

        if self.store is None:
            return []

        # Create a list of dictionaries containing product details
        products_list = []
        for product in self.store.products:
            product_info = {
                "product_id": product.product_id,
                "product_name": product.product_name,
                "price": product.price,
                "quantity": product.quantity,
                "description": product.description,
                "category": product.category,
                "image_paths": product.image_paths,
                "variations": product.variations,
            }
            products_list.append(product_info)

        return products_list