from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from django.conf import settings
from django.core.management.base import BaseCommand
import psycopg2

class Command(BaseCommand):
    help = 'Starts the Telegram bot'

    def handle(self, *args, **options):
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

        def start(update: Update, context):
            keyboard = [
                [InlineKeyboardButton("Stupid", callback_data='stupid'),
                 InlineKeyboardButton("Fat", callback_data='fat'),
                 InlineKeyboardButton("Dumb", callback_data='dumb')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Press a button:", reply_markup=reply_markup)

        def button(update: Update, context):
            query = update.callback_query
            button_name = query.data
            user_id = query.from_user.id
            with conn, conn.cursor() as cursor:
                cursor.execute('INSERT INTO button_presses (user_id, button_name) VALUES (%s, %s)', (user_id, button_name))
            query.answer()
            query.edit_message_text(text=f"Button {button_name} pressed")

        updater = Updater(token=settings.TELEGRAM_BOT_TOKEN, use_context=True)
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(CallbackQueryHandler(button))
        updater.start_polling()
       
