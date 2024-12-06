import os
import requests
from telegram import Update, InputFile  # Added InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Replace with your Telegram bot token and admin chat ID
TELEGRAM_TOKEN = '7927024454:AAHYbph3KPAW0R8-KT-hgujnO28ZqqL9-Y0'
ADMIN_CHAT_ID = [6715273029,387387398,827152976]
# Define conversation states
NAME, CONTACT, COMPLAINT, IMAGE = range(4)


def start(update: Update, context: CallbackContext):
    update.message.reply_text("እንኳን ደህና መጡ! እባክዎን ስምዎን ያስገቡ:")
    return NAME


def get_name(update: Update, context: CallbackContext):
    context.user_data['name'] = update.message.text
    update.message.reply_text( "እናመሰግናለን, {}! እባክዎን ስልክ  ቁጥርዎን ያስገቡ :".format(
            update.message.text))
    return CONTACT


def get_contact(update: Update, context: CallbackContext):
    context.user_data['contact'] = update.message.text
    update.message.reply_text("እባክዎን ቅሬታዎን ግለጹ:")
    return COMPLAINT


def get_complaint(update: Update, context: CallbackContext):
    context.user_data['complaint'] = update.message.text
    update.message.reply_text("ፋይል ካለዎት አታች ያርጉ ከሌልዎት  /end በማለት ይጨርሱ.")
    return IMAGE


def get_image(update: Update, context: CallbackContext):
    if update.message.photo:
        file_id = update.message.photo[
            -1].file_id  # Get the highest quality photo
        new_file = context.bot.get_file(file_id)
        file_path = f"complaint_image_{update.message.from_user.id}.jpg"
        new_file.download(file_path)

        context.user_data['image_path'] = file_path

        # Send the image to the admin
        image_file = InputFile(open(file_path, 'rb'))  # Create InputFile object
        for admin_id in ADMIN_CHAT_ID:
            context.bot.send_photo(chat_id=admin_id, photo=image_file)  # Send with InputFile

    else:
        context.user_data['image_path'] = None


# Notify the admin with all collected data
    notify_admin(context.user_data)

    update.message.reply_text("ስለ ቅሬታዎ እናመሰግናለን! በቅርቡ ቅሬታዎ በሚመለከተው አካል የሚታይ ይሆናል")
    update.message.reply_text("እናመሰግናለን ! ቅሬታዎ ተመዝግቧል /start የሚለዉን በመላክ አዲስ ቅሬታ ማቅረብ  ይችላሉ")
    return ConversationHandler.END


def end(update: Update, context: CallbackContext):
    notify_admin(context.user_data)
    update.message.reply_text("እናመሰግናለን ! ቅሬታዎ ተመዝግቧል /start የሚለዉን በመላክ አዲስ ቅሬታ ማቅረብ  ይችላሉ.")
    return ConversationHandler.END


def notify_admin(user_data):
    message = (
        f"አዲስ ቅሬታ ደረሰ :\n"
        f"ስም: {user_data['name']}\n"
        f"ስልክ: {user_data['contact']}\n"
        f"ቅሬታ: {user_data['complaint']}\n"
        # f"File: {user_data.get('file_path', 'No file uploaded')}"
        f"ፋይል: {user_data.get('image_path', 'No image uploaded')}")
    for admin_id in ADMIN_CHAT_ID:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={
                "chat_id": admin_id,
                "text": message
            })


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("ውይይት ተሰርዟል")
    return ConversationHandler.END


# Set up the conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
        CONTACT:
        [MessageHandler(Filters.text & ~Filters.command, get_contact)],
        COMPLAINT:
        [MessageHandler(Filters.text & ~Filters.command, get_complaint)],
        #FILE: [MessageHandler(Filters.document, get_file)],
        IMAGE: [MessageHandler(Filters.photo, get_image)],
    },
    fallbacks=[CommandHandler('end', end),
               CommandHandler('cancel', cancel)],
)

# Initialize the bot
updater = Updater(TELEGRAM_TOKEN)
updater.dispatcher.add_handler(conv_handler)

# Start polling
updater.start_polling()
updater.idle()
