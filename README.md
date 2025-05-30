## Телеграм-бот для получения информации через текстовый и голосовой ввод

### Цель проекта

Создание Telegram-бота, который позволяет пользователям получать информацию с помощью сервиса ChatGPT, используя как текстовый, так и голосовой ввод запросов.

---

### Как пользоваться

1. Найдите бота в Telegram по имени: `voice_text_GPT` или перейдите по ссылке: [t.me/voice_text_GPT](https://t.me/voice_text_GPT).

2. Для начала работы:
   - Нажмите кнопку меню `/start`,
   - или сразу введите текстовый запрос,
   - или отправьте голосовое сообщение.

3. **Текстовый запрос:**
   - Введите ваш запрос в чате.
   - Бот обработает его и вернёт ответ от ChatGPT.

4. **Голосовой запрос:**
   - Отправьте голосовое сообщение.
   - Бот преобразует речь в текст, покажет его, а затем отправит ответ от ChatGPT.

---

### Технические требования

- Python 3.10+
- Установленные библиотеки:
  - `telebot`
  - `SpeechRecognition`
- Аккаунт OpenAI с API-ключом
- Токен Telegram-бота

---

## Инструкция по развёртыванию

1.  **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/i-koskin/ChatGPT_Bot.git
   cd ChatGPT_Bot
   ```

2.  **Создайте и активируйте виртуальное окружение (по желанию):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   venv\Scripts\activate     # для Windows
   ```

3.  **Установите зависимости:**

   ```bash
   pip install -r requirements.txt
   ```

4.  **Запустите бота:**

   ```bash
   python main.py
   ```
