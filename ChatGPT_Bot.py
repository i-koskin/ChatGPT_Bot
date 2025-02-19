import telebot
import requests
import json
import speech_recognition as sr
import os
import subprocess
import datetime
import logging
from telebot import types
from dotenv import load_dotenv, find_dotenv

class CHATGPT:
    def __init__(self, api_key):
        self.api_key = api_key  # Сохраняем API-ключ
        self.messages = []  # Инициализируем историю сообщений

    def get_message(self, message):
        # Добавляем сообщение пользователя в историю сообщений
        self.messages.append({'role': 'user', "content": message})

        # Устанавливаем заголовки для запроса к API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Создаем тело запроса
        body = {
            "model": "gpt-4o-mini",  
            "messages": self.messages,  
            "max_tokens": 1000,  # Максимальное количество токенов в ответе
            "temperature": 0.7  # Параметр "температура" для управления креативностью ответов
        }

        # Преобразуем тело запроса в формат JSON
        jsondata = json.dumps(body, ensure_ascii=False).encode('UTF8')

        # Отправляем POST-запрос к API OpenAI
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=jsondata)

        # Проверяем успешность ответа
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']  # Извлекаем ответ ассистента
            # Добавляем ответ ассистента в историю сообщений
            self.messages.append({'role': 'assistant', "content": answer})
            return answer  
        else:
            # Обрабатываем случай ошибки
            print(f"Ошибка: {response.status_code} - {response.text}")  # Выводим ошибку в консоль
            return "Произошла ошибка при получении ответа." 

# Загрузка переменных окружения из файла .env
load_dotenv(find_dotenv())
# Создаем экземпляр CHATGPT с API-ключом из переменной окружения
chatgpt = CHATGPT(os.getenv('chat_gpt_api_key'))
# Создаем экземпляр бота Telegram с токеном из переменной окружения
bot = telebot.TeleBot(os.getenv('TOKEN'))
bot.retry_timeout = 30  # Устанавливаем тайм-аут для повторных попыток
bot.num_retries = 3  # Устанавливаем максимальное количество повторных попыток
logfile = str(datetime.date.today()) + '.log'  # Имя файла для логирования

# Настройка конфигурации логирования
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Функция для перевода аудио в текст
def audio_to_text(dest_name: str):
    r = sr.Recognizer()  # Создаем распознаватель
    message = sr.AudioFile(dest_name)  
    with message as source:  
        audio = r.record(source)  
    result = r.recognize_google(audio, language="ru_RU")  # Преобразуем аудио в текст с помощью Google API
    return result  

@bot.message_handler(commands=['start'])  # Обработчик команды /start
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создаем разметку клавиатуры

    # Добавление кнопок
    item1 = types.KeyboardButton("/start")  
    item2 = types.KeyboardButton("Написать текст")  
    item3 = types.KeyboardButton("Отправить аудио")  
    item4 = types.KeyboardButton("/help")  
    item5 = types.KeyboardButton("/stop")  

    # Добавляем кнопки в разметку
    markup.add(item1, item2, item3, item4, item5)

    # Отправляем приветственное сообщение с клавиатурой
    bot.send_message(message.chat.id, "Чтобы начать взаимодействие с ботом выберите пункт меню ⬇️ или начните писать сообщение...",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Написать текст") 
def handle_text(message):
    bot.send_message(message.chat.id, "✍️ Введите текстовый запрос и я отвечу Вам.")  

@bot.message_handler(func=lambda message: message.text == "Отправить аудио")  #
def handle_audio(message):
    bot.send_message(message.chat.id, "📢 Чтобы отправить голосовой запрос, нажмите на значок микрофона в интерфейсе чата и запишите свое сообщение.\n Я преобразую запрос в текст и отвечу Вам.\n")

@bot.message_handler(commands=['help'])  # Обработчик команды /help
def help_message(message):
    # Отправляем сообщение с инструкциями по использованию бота
    bot.send_message(message.chat.id, "Это бот, который поможет вам общаться с ChatGPT, отправляя текстовые или голосовые запросы. \n\n" \
               "✍️ При отправке текстового запроса введите сообщение и отправьте его. Бот ответит ответом, сгенерированным моделью ChatGPT.\n" \
               "📢 Чтобы отправить голосовой запрос, нажмите на значок микрофона в интерфейсе чата и запишите свое сообщение. Как только вы закончите, отправьте его. Бот преобразует звук в текст с помощью распознавания речи, отправит текст в модель ChatGPT и ответит.\n " \
               "⏱️ Будьте терпеливы, ожидая ответа от бота, особенно для длинных сообщений или голосовых/аудиосообщений. Боту нужно время, чтобы обработать и сгенерировать осмысленный ответ.\n " \
               "☝️ Формулируйте свои запросы четкими и краткими, чтобы получать от бота наиболее точные и актуальные ответы")

# Флаг для остановки опроса
stop_polling = False

@bot.message_handler(commands=['stop'])  # Обработчик команды /stop
def stop_polling_handler(message):
    # Отправляем сообщение о приостановке работы бота
    bot.send_message(message.chat.id, "⛔️ Бот остановлен.")
    global stop_polling
    stop_polling = True  

@bot.message_handler(content_types=['text'])  # Обработчик текстовых сообщений
def message_reply(message):
    # Проверяем, что сообщение не является командой или специальным текстом
    if message.text not in ['/start', '/help', '/stop', 'Написать текст', 'Отправить аудио']:
        bot.send_message(message.chat.id, '🌀 Генерируем ответ...')  
        answer = chatgpt.get_message(message.text)  
        bot.send_message(message.chat.id, answer)  

@bot.message_handler(content_types=['voice', 'audio'])  # Обработчик голосовых сообщений
def voice_processing(message):
    bot.send_message(message.chat.id, '🌀 Преобразуем запрос в текст...')  
    try:
        file_info = bot.get_file(message.voice.file_id)  # Получаем информацию о файле голосового сообщения
        path = file_info.file_path  
        fname = os.path.basename(path)  
        # Загружаем аудиофайл с сервера Telegram
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(os.getenv('TOKEN'), file_info.file_path))
        with open(fname + '.oga', 'wb') as f:
            f.write(doc.content)  

        # Конвертируем файл OGA в WAV с помощью FFmpeg
        process = subprocess.run(['ffmpeg', '-i', fname + '.oga', fname + '.wav'], capture_output=True)
        if process.returncode != 0:  # Проверяем успешность конвертации
            raise Exception(f"FFmpeg conversion failed: {process.stderr.decode()}")
            
        if os.path.exists(fname + '.wav'):  
            result = audio_to_text(fname + '.wav')  
            bot.send_message(message.from_user.id, f"Ваш запрос: \n {result}")  
            bot.send_message(message.chat.id, '🌀 Генерируем ответ...')  
            answer = chatgpt.get_message(result)  
            bot.send_message(message.chat.id, answer) 
        else:
            raise Exception("WAV file was not created") 

    except sr.UnknownValueError as e:  # Обработка ошибок распознавания речи
        bot.send_message(message.from_user.id, "🤷‍♂️ Прошу прощения, но я не разобрал сообщение, или оно пустое...")
        # Логируем ошибку
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(
                message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(
                message.from_user.username) + ':' + str(message.from_user.language_code) + ':Message is empty.\n')
    except Exception as e:  # Обработка других исключений
        bot.send_message(message.from_user.id, "🤷‍♂️ Прошу прощения, но я не разобрал сообщение, или оно пустое...")
        # Логируем ошибку
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(
                message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(
                message.from_user.username) + ':' + str(message.from_user.language_code) + ':' + str(e) + '\n')
    finally:
        # Удаляем временные файлы
        if os.path.exists(fname + '.wav'):
            os.remove(fname + '.wav')
        if os.path.exists(fname + '.oga'):
            os.remove(fname + '.oga')


def main():
    try:
        # Очищаем webhook, чтобы убедиться, что предыдущие экземпляры не работают
        bot.remove_webhook()
        logging.info("Бот запущен")
        # Запускаем опрос с параметром non_stop=True для обработки переподключений
        bot.infinity_polling(none_stop=True, interval=1, timeout=60)
    except Exception as e:
        logging.error(f"Ошибка при опросе бота: {e}")
    finally:
        try:
            # Останавливаем опрос бота
            bot.stop_polling()
            logging.info("Бот остановлен")
        except Exception as e:
            logging.error(f"Ошибка при остановке бота: {e}")

if __name__ == "__main__":
    main()
