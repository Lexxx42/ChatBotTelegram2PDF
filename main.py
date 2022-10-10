import os
import os.path

from send_doc import send_document
from start_bot import bot
from clear_catalog import clear_catalog
from txt_to_pdf import convert_text_pdf
from excel_to_pdf import excel_to_pdf
from datetime import datetime

local_src = ""
SRC = './tmp_files/'


# 2 реакции на команды для бота.
@bot.message_handler(commands=['start', 'help', 'info'])  # tab-ы не трогать!
def send_welcome(message):
    if message.text == '/help':
        bot.reply_to(message, '''Список поддерживаемых конверсий:
* .txt -> .pdf ( Поддерживаемые кодировки: ANSI, UTF-8 )
* .jpg -> .pdf
''')
    elif message.text == '/start':
        bot.reply_to(message, '''Этот бот конвертирует файлы с различными расширениями в pdf.\n
Чтобы посмотреть список поддерживаемых конвертий используйте /help''')
    else:
        bot.reply_to(message, '''Бот-конвертер(тут будет клевое название) - это некоммерческий проект.
Создан исключетельно на энтузиазме и любви к разработке.\n
Бот принимает файл, конвертирует его и отправляет обратно пользователю.
После чего удаляет ваш файл с сервера и очищает директорию.
Бот не собирает никакие данные о пользователе и не сохраняет никакую информацию.
Статистика работы и обработки сценариев не ведется.
Мы уважаем конфиденциальность информации пользователей и поддерживаем политику telegram в отношении приватности.\n
Если вам нравится (имя) и вы хотите подкинуть нам денег на кофе ☕
То поддержите проект, отправив на (реквезиты) произвольную сумму в рублях.
Мы сделали этот проект для вас и для наших друзей и близких! Приятного использования 😇''')


# Чат бот принимает файлы.
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    """
    сохранение любого типа файла на компьютер в указанную директорию
    :type message: object
    """
    try:
        chat_id = message.chat.id
        # получаем имя и расширение файла, так что бы пронести переменные до конца
        real_file_name, real_file_extension = os.path.splitext(message.document.file_name)
        file_name = real_file_name.lower()
        file_extension = real_file_extension.lower()
        # TODO: доделать так что бы сначала была папку с чат айди потом внутри папки с оригиналами файлов
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = SRC + file_name + '_' + str(chat_id) + '_' + str(datetime.today().strftime('%Y-%m-%d %H-%M-%S'))
        # создаем папку в которой будем временно размещать файл, если таковой не существует
        if not os.path.exists(src):
            os.makedirs(src)
        # создаем путь конечного файла - думаю надо переделать - это временный вариант
        local_src = src + '/' + real_file_name + real_file_extension
        # пишем файл на диск
        with open(local_src, 'wb') as new_file:
            new_file.write(downloaded_file)

        if file_extension == '.txt':  # проверяем расширение txt
            bot.reply_to(message, "Конвертирую 😉")
            convert_text_pdf(local_src)
            send_document(convert_text_pdf(local_src), chat_id)
        elif file_extension == '.xls' or '.xlsx':  # проверяем расширение excel
            bot.reply_to(message, "xls")
        elif file_extension == '.doc' or '.docx':  # проверяем расширение excel
            bot.reply_to(message, "doc")
        elif file_extension == '.jpg' or '.jpeg' or '.png' or '.tiff' or '.jpg2' or '.heif' or '.heic':
            # отсылаем файл пользователю (используем модуль конвертера)
            send_document(img_2_pdf(local_src, message), chat_id)
        else:
            bot.reply_to(message, f"я не знаю такого '{file_extension}' формата 😶‍🌫️😇")
        clear_catalog(
            src)  # ВНИМАНИЕ! теперь функция удаляет и файлы и папки - пути писать аккуратно что бы не затерло системные файлы
    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(func=lambda message: True)  # Бот на любое сообщение пользователя, кроме файла
# и команды отвечает списком всех доступных команд.
def echo(message):  # нельзя трогать tab-ы у текста!
    chat_id = message.from_user.id  # user_id берется из id_сообщения.
    text = '''Основные команды:
/start - Приветствие
/help - Список возможных конверсий
/info - Пояснения о работе бота'''
    bot.send_message(chat_id, text)


bot.polling(none_stop=True, interval=0)
