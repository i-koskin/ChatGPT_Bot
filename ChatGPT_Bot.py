import telebot
import requests
import json
import speech_recognition as sr
import os
import subprocess
import datetime
from telebot import types
from dotenv import load_dotenv, find_dotenv


class CHATGPT:
    def __init__(self, chatgpt_api_key):
        self.messages = []
        self.api_key = chatgpt_api_key

    def get_message(self, message):
        self.messages.append({'role': 'user', "content": message})
        headers = {"Authorization": self.api_key, "Content-Type": "application/json"}
        body = {
            "model": "gpt-3.5-turbo",
            "messages": self.messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        jsondata = json.dumps(body, ensure_ascii=False).encode('UTF8')
        web = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=jsondata)
        answer = web.json()['choices'][0]['message']['content']
        self.messages.append({'role': 'assistant', "content": answer})
        return answer


load_dotenv(find_dotenv())
chatgpt = CHATGPT(os.getenv('chat_gpt_api_key'))
bot = telebot.TeleBot(os.getenv('TOKEN'))
logfile = str(datetime.date.today()) + '.log'


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
    item1 = types.KeyboardButton("/help")
    markup.add(item1)
    bot.send_message(message.chat.id,
                     "Привет ✌ \n Давай пообщаемся с GPT3. \n Можешь написать текст или отправить аудио.",
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def message_reply(message):
    if message.text == "/help":
        help = "Вы можете общаться с ботом, отправляя текстовые или голосовые сообщения. \n\n" \
               "✍При отправке текстового сообщения просто введите сообщение и отправьте его. Бот ответит ответом, сгенерированным моделью ChatGPT.\n" \
               "📢Чтобы отправить голосовое сообщение, нажмите на значок микрофона в интерфейсе чата и запишите свое сообщение. Как только вы закончите, отправьте его. Бот преобразует звук в текст с помощью распознавания речи, отправит текст в модель ChatGPT и ответит.\n " \
               "🤌Будьте терпеливы, ожидая ответа от бота, особенно для длинных сообщений или голосовых/аудиосообщений. Боту нужно время, чтобы обработать и сгенерировать осмысленный ответ.\n " \
               "☝Сохраняйте свои сообщения четкими и краткими, чтобы получать от бота наиболее точные и актуальные ответы. Избегайте двусмысленных или неполных предложений.\n" \
               "😉Наслаждайтесь общением с ботом Telegram и отлично проведите время!"
        bot.send_message(message.chat.id, help)
    else:
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
