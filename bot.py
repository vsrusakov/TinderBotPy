from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from local_settings import TG_BOT_TOKEN, OPEN_AI_TOKEN
from gpt import *
from util import *


async def start(update, context):
    dialog.mode = 'main'
    text = load_message('main')
    await send_photo(update, context, 'main')
    await send_text(update, context, text)

    await show_main_menu(update, context, {
        'start': 'главное меню бота',
        'profile': 'генерация Tinder-профля 😎',
        'opener': 'сообщение для знакомства 🥰',
        'message': 'переписка от вашего имени 😈',
        'date': 'переписка со звездами 🔥',
        'gpt': 'задать вопрос чату GPT 🧠',
    })


async def gpt(update, context):
    dialog.mode = 'gpt'
    text = load_message('gpt')
    await send_photo(update, context, 'gpt')
    await send_text(update, context, text)


async def gpt_dialog(update, context):
    text = update.message.text
    prompt = load_message('gpt')
    answer = await char_gpt.send_question(prompt, text)
    await send_text(update, context, answer)


async def hello(update, context):
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    else:
        await send_text(update, context, '*привет, привет!*')
        await send_text(update, context, '_как дела?_')
        await send_text(update, context, f'вы написали: _{update.message.text}_')

        await send_photo(update, context, 'avatar_main')
        await send_text_buttons(update, context, 'Запустить процесс?', {
            'start': 'Запустить',
            'stop': 'Остановить',
        })


async def hello_button(update, context):
    query = update.callback_query.data
    if query == 'start':
        await send_text(update, context, 'Процесс запущен')
    else:
        await send_text(update, context, 'Процесс остановлен')


dialog = Dialog()
dialog.mode = None
char_gpt = ChatGptService(token=OPEN_AI_TOKEN)

app = ApplicationBuilder().token(TG_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CallbackQueryHandler(hello_button))
app.run_polling()
