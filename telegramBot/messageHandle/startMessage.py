from telegram import Update, Bot, File, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters,CallbackContext, CallbackQueryHandler
from telegram.constants import ParseMode
#from DatabaseHandle.database import execute_query





async def start(update: Update, context: CallbackContext) -> None:
    print("Un utilisateur :", update.message.from_user)
    telegram_user_id = update.message.from_user.id
    
        
    #query = f"SELECT * FROM users WHERE telegram_id = {telegram_user_id}"
    #userKain = execute_query(query)

    #if userKain:
        
    #    await update.message.reply_text("User already exists!")
    #    return
    

    keyboard = [
        [InlineKeyboardButton("Darija 🇲🇦", callback_data='1')],
        [InlineKeyboardButton("English 🇬🇧", callback_data='2'),
        InlineKeyboardButton("French 🇫🇷", callback_data='3')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    with open('C:/Users/Hamza/Desktop/Messy Desktop that i had/enhancedLogo.png', 'rb') as photo:
        await update.message.reply_photo(photo=photo,
                                         caption=f"Salam {update.message.from_user.first_name} Awl mara hna ?? first time i think right ? well, m3ak Easy! Choose a langauage to go with bach nbdaw...",
                                         reply_markup=reply_markup,
                                         parse_mode=ParseMode.HTML)