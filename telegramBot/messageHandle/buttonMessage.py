from telegram import Update, Bot, File, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters,CallbackContext, CallbackQueryHandler
from telegram.constants import ParseMode

user_language = {}  


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  
    print('hachno tkhtar ', query.data)

    language_map = {'1': 'Darija', '2': 'English', '3': 'French'}
    
    if query.data in language_map:

        chosen_language = language_map[query.data] # type: ignore

        user_language[query.from_user.id] = chosen_language  # Set the language for the user

            
        if chosen_language == "Darija":
            await query.edit_message_caption(caption=f"Thank you for choosing {chosen_language} !!")

            syscontext = "You are a storage management bot, your name is 'Easy' and you are here to help the user manage his storage. The user just used 'Darija'."
            #await query.message.reply_text(answer(syscontext, None))

        elif chosen_language == "English":
            await query.edit_message_caption(caption=f"Thank you for choosing {chosen_language}  🇬🇧 !!")

            syscontext = "You are a storage management bot, your name is 'Easy' and you are here to help the user manage his storage. The user just used 'English' as a chat language. The System is named EasyFind, and you will help him reach more clients, add emojis to the reply. and ask also about his store infos"
            #the bot in here is done safi dar introduction lrasso o swl 3la magasin db chno khass ? khass user ijwb 3la store info bach idkhlo la BD, fin ghyjwb ? handle_message tmak 
            await query.message.reply_text("YAAAAW ENGLISH")
            

        elif chosen_language == "French":
            syscontext = "You are a storage management bot, your name is 'Easy' and you are here to help the user manage his storage. The user just used 'French' as a chat language."
            #await query.message.reply_text(answer(syscontext, None))