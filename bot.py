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
    answer = await chat_gpt.send_question(prompt, text)
    await send_text(update, context, answer)


async def date(update, context):
    dialog.mode = 'date'
    text = load_message('date')
    await send_photo(update, context, 'date')
    await send_text_buttons(update, context, text, {
        'date_grande': 'Ариана Гранде',
        'date_robbie': 'Марго Робби',
        'date_zendaya': 'Зендея',
        'date_gosling': 'Райан Гослинг',
        'date_hardy': 'Том Харди',
    })


async def date_dialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, 'Девушка набирает сообщение...')
    answer = await chat_gpt.add_message(text)
    await my_message.edit_text(answer)


async def date_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    await send_photo(update, context, query)
    await send_html(update, context, 'Отличный выбор! Пригласите девушку '
                                     '(парня) на свидание за пять сообщений')

    prompt = load_prompt(query)
    chat_gpt.set_prompt(prompt)


async def message(update, context):
    dialog.mode = 'message'
    text = load_message('message')
    await send_photo(update, context, 'message')
    await send_text_buttons(update, context, text, {
        'message_next': 'Следующее сообщение',
        'message_date': 'Пригласить на свидание',
    })
    dialog.list.clear()


async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = '\n\n'.join(dialog.list)
    my_message = await send_text(update, context, 'ChatGPT думает над ответом...')
    answer = await chat_gpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)


async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)


async def hello(update, context):
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    elif dialog.mode == 'date':
        await date_dialog(update, context)
    elif dialog.mode == 'message':
        await message_dialog(update, context)
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
dialog.list = []

chat_gpt = ChatGptService(token=OPEN_AI_TOKEN)

app = ApplicationBuilder().token(TG_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('date', date))
app.add_handler(CommandHandler('message', message))

app.add_handler(CallbackQueryHandler(date_button, pattern='^date_.*'))
app.add_handler(CallbackQueryHandler(message_button, pattern='^message_.*'))
app.add_handler(CallbackQueryHandler(hello_button))

app.run_polling()
