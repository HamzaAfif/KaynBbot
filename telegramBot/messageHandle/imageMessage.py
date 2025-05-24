from telegram import Update, Bot, File, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters,CallbackContext, CallbackQueryHandler
from telegram.constants import ParseMode

from datetime import datetime
import requests
import os 
import uuid

from messageHandle.textMessage import run_conversation, get_or_create_session
from messageHandle.textMessage import User, Session
from subProc.addImages import associate_image_with_product_via_history
from subProc.imgTest import process_image
from subProc.checkProductState import check_if_adding_product
from subProc.imageProductManager import manage_image_product_association

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Image received. Please hold on while I process it... 📸")

    user_id = update.message.from_user.id
    session = get_or_create_session(user_id)

    photo = update.message.photo[-1]
    file: File = await context.bot.get_file(photo.file_id)

    download_url = f"{file.file_path}"
    save_directory = f"data/pictures/products/user_{user_id}"
    os.makedirs(save_directory, exist_ok=True)

    filename = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(save_directory, filename)

    response = requests.get(download_url)

    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        clean_image_path = process_image(file_path)

        session.add_unassociated_image_path(clean_image_path)
        system_message = "The image has been successfully processed and saved! 🖼️ Now, please provide the product details."
        assistant_reply = run_conversation(
            user_message=system_message,
            user_id=update.message.from_user.id,
            system_message=system_message
        )
        await update.message.reply_text(assistant_reply)

    else:
        system_message = "Failed to download image. Please try again."
        
        assistant_reply = run_conversation(
            user_message=system_message,
            user_id=update.message.from_user.id,
            system_message=system_message
        )
        await update.message.reply_text(assistant_reply)

    incomplete_product_details = session.get_incomplete_product_details()
    unassociated_images = session.get_unassociated_image_paths()

    if incomplete_product_details or unassociated_images:
        association_response = manage_image_product_association(
            question="Link image with product",
            unassociated_images=unassociated_images,
            incomplete_product_details=incomplete_product_details
        )

        # If the response has valid product details, finalize the entry
        if association_response.get("status"):
            product_name = association_response["product_name"]
            session.user.add_product_to_store(
                product_name=product_name,
                price=association_response["price"],
                quantity=association_response["quantity"],
                description=association_response["description"],
                category=association_response["category"],
                variations=association_response["variations"]
            )

            for image_path in association_response["image_paths"]:
                session.user.add_image_to_product(product_name, image_path)

            session.clear_unassociated_image_paths()
            session.clear_incomplete_product_details()

            assistant_reply = f"Product '{product_name}' has been successfully created/updated with images! ✅"
            assistant_reply = run_conversation(
                user_message=system_message,
                user_id=update.message.from_user.id,
                system_message=system_message
            )
            await update.message.reply_text(assistant_reply)