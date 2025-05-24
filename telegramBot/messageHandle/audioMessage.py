from telegram import Update, Bot, File, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters,CallbackContext, CallbackQueryHandler
from telegram.constants import ParseMode

from subProc.audioToText import audio_to_text
from messageHandle.textMessage import run_conversation
from subProc.textToAudio import text_to_audio

import requests
import os 
from datetime import datetime

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Sifti audioo ! Easy is listening to it...")

    print('audio sent mn3and:', update.message.from_user)

    file_id = update.message.voice.file_id
    file: File = await context.bot.get_file(file_id)

    download_url = f"{file.file_path}"
    print(download_url)

    save_directory = f"data/audios/{update.message.from_user.id}"
    os.makedirs(save_directory, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(save_directory, f"{timestamp}.ogg")

    response = requests.get(download_url)
    if response.status_code == 200:
        with open(file_path, 'wb') as audio_file:
            audio_file.write(response.content)
        await update.message.reply_text(f"Safii! test check audio wssl saved o kolchi")
        
        transcribed_text = audio_to_text(file_path)
        await update.message.reply_text(f"Audio to text: {transcribed_text}")
        
        assistant_reply = run_conversation(transcribed_text, update.message.from_user.id)
        await update.message.reply_text(f"Text message dial easy: {assistant_reply}")
        
        output_audio_file = os.path.join(save_directory, f"reply_audio_{timestamp}.mp3")
        text_to_audio(assistant_reply, output_file=output_audio_file)
        
        await update.message.reply_audio(audio=open(output_audio_file, 'rb'))
        
    else:
        await update.message.reply_text("Kin chi mochkill")
        
       