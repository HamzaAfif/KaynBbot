from rembg import remove
from PIL import Image, ImageOps
import io
import os

with open('C:/Users/Hamza/Desktop/Messy Desktop that i had/photo test.jpg', 'rb') as file:
    input_image = file.read()

output_image = remove(input_image)

with open('output_image.png', 'wb') as file:
    file.write(output_image) # type: ignore


from rembg import remove
from PIL import Image, ImageOps
import io
import os


def process_image(input_file_path: str, output_file_path: str = None) -> str:
    
    with open(input_file_path, 'rb') as file:
        input_image = file.read()

    output_image = remove(input_image)

    image = Image.open(io.BytesIO(output_image))

    desired_width = 1200

    aspect_ratio = image.width / image.height
    desired_height = int(desired_width / aspect_ratio)

    image = image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)

    if image.mode in ('RGBA', 'LA'):  
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3]) 
        image = background

    image = ImageOps.pad(image, (desired_width, desired_height), color='white')

    if not output_file_path:
        base, ext = os.path.splitext(input_file_path)
        output_file_path = f"{base}_processed{ext}"

    image.save(output_file_path, 'JPEG', quality=85, optimize=True)

    print("Image processing complete: Background removed, resized, and optimized for e-commerce.")
    return output_file_path


#input_path = 'C:/Users/Hamza/Desktop/Messy Desktop that i had/photo test.jpg'
#output_path = process_image(input_path)
#print(f"Processed image saved to: {output_path}")