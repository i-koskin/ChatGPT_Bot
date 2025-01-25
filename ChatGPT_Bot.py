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
        self.api_key = api_key
        self.messages = []

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
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        # Преобразуем тело в формат JSON
        jsondata = json.dumps(body, ensure_ascii=False).encode('UTF8')
        
        # Отправляем POST-запрос к API OpenAI
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=jsondata)
        
        # Проверяем успешность ответа
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            # Добавляем ответ ассистента в историю сообщений
            self.messages.append({'role': 'assistant', "content": answer})
            return answer
        else:
            # Обрабатываем случай ошибки
            print(f"Ошибка: {response.status_code} - {response.text}")
            return "Произошла ошибка при получении ответа."

load_dotenv(find_dotenv())
chatgpt = CHATGPT(os.getenv('chat_gpt_api_key'))
bot = telebot.TeleBot(os.getenv('TOKEN'))
logfile = str(datetime.date.today()) + '.log'

# Настройка логирования
logging.basicConfig(level=logging.ERROR)

# Функция для перевода аудио, в формате ".vaw" в текст
def audio_to_text(dest_name: str):
    r = sr.Recognizer()
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU")
    return result

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Добавление кнопок
    item1 = types.KeyboardButton("/start")
    item2 = types.KeyboardButton("Написать текст")
    item3 = types.KeyboardButton("Отправить аудио")
    item4 = types.KeyboardButton("/help")
    item5 = types.KeyboardButton("/stop")
    
    # Добавляем кнопки в разметку
    markup.add(item1, item2, item3, item4, item5)

    bot.send_message(message.chat.id,
                     "Привет ✌️ \nДавай пообщаемся с GPT-4. \nВыбери опцию ниже:",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Написать текст")
def handle_text(message):
    bot.send_message(message.chat.id, "Введите текст, и я отвечу вам.")

@bot.message_handler(func=lambda message: message.text == "Отправить аудио")
def handle_audio(message):
    bot.send_message(message.chat.id, "📢 Чтобы отправить голосовое сообщение, нажмите на значок микрофона в интерфейсе чата и запишите свое сообщение.\n\
        Бот преобразует звук в текст с помощью распознавания речи, отправит текст в модель ChatGPT и ответит.\n")

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "Это бот, который поможет вам общаться с GPT-4. Вы можете написать текст или отправить аудио.")

# Флаг для остановки опроса
stop_polling = False

@bot.message_handler(commands=['stop'])
def stop_polling_handler(message):
    bot.reply_to(message, "Бот остановлен.")
    global stop_polling
    stop_polling = True

def run_bot():
    while not stop_polling:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка: {e}")

@bot.message_handler(content_types=['text'])
def message_reply(message):
    bot.send_message(message.chat.id, '🌀 Генерируем ответ...')
    answer = chatgpt.get_message(message.text)
    bot.send_message(message.chat.id, answer)

@bot.message_handler(content_types=['voice', 'audio'])
def voice_processing(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        path = file_info.file_path
        fname = os.path.basename(path)
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(os.getenv('TOKEN'), file_info.file_path))
        with open(fname + '.oga', 'wb') as f:
            f.write(doc.content)
        process = subprocess.run(['ffmpeg', '-i', fname + '.oga', fname + '.wav'])
        result = audio_to_text(fname + '.wav')
        bot.send_message(message.from_user.id, f" Ваш запрос: \n {result}")
        bot.send_message(message.chat.id, '🌀 Генерируем ответ...')
        answer = chatgpt.get_message(result)
        bot.send_message(message.chat.id, answer)

    except sr.UnknownValueError as e:
        bot.send_message(message.from_user.id, "Прошу прощения, но я не разобрал сообщение, или оно пустое...")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(
                message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(
                message.from_user.username) + ':' + str(message.from_user.language_code) + ':Message is empty.\n')
    except Exception as e:
        bot.send_message(message.from_user.id, "Прошу прощения, но я не разобрал сообщение, или оно пустое...")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(
                message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(
                message.from_user.username) + ':' + str(message.from_user.language_code) + ':' + str(e) + '\n')
    finally:
        os.remove(fname + '.wav')
        os.remove(fname + '.oga')

bot.infinity_polling()
