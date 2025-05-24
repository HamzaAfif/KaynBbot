import uuid

class Product:
    def __init__(self, product_name, price, quantity, description, category="", image_paths=None, product_id=None, variations=None):
        self.product_id = product_id or str(uuid.uuid4())  
        self.product_name = product_name
        self.price = price
        self.quantity = quantity
        self.description = description
        self.category = category
        self.image_paths = image_paths or []
        self.variations = variations or []  # List of variations (e.g., sizes and quantities)

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "price": self.price,
            "quantity": self.quantity,
            "description": self.description,
            "category": self.category,
            "image_paths": self.image_paths,
            "variations": self.variations  # Include variations in the dictionary
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            product_name=data.get("product_name"),
            price=data.get("price"),
            quantity=data.get("quantity"),
            description=data.get("description"),
            category=data.get("category", ""),
            image_paths=data.get("image_paths", []),
            product_id=data.get("product_id"),
            variations=data.get("variations", [])
        )
