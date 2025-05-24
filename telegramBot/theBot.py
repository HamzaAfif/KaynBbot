from telegram import Update, Bot, File, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters,CallbackContext, CallbackQueryHandler
from telegram.constants import ParseMode

from messageHandle.startMessage import start
from messageHandle.buttonMessage import button
from messageHandle.textMessage import handle_message
from messageHandle.audioMessage import handle_audio
from messageHandle.imageMessage import handle_image
from messageHandle.locationMessage import handle_location
from dotenv import load_dotenv


load_dotenv('.env')


telegramToken: str = "7068342140:AAHJ6i20IvAi9dN1WLG8ri53kZB-QUjpu2o"  




def main() -> None:
    application = Application.builder().token(telegramToken).build()

    print("BOT marche")


    application.add_handler(CommandHandler("start", start))

    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_audio))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))


    #application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    application.run_polling()
    
main()