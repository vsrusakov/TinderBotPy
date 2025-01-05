from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from local_settings import TELEGRAM_BOT_KEY
from gpt import *
from util import *


app = ApplicationBuilder().token(TELEGRAM_BOT_KEY).build()
app.run_polling()
