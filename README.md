# ChatGPT_Bot
Проект "Телеграм-бот для получения информации через текстовый и голосовой ввод запроса"

Цель проекта:
Создание и размещение Телеграм-бота, который позволяет пользователям получать интересующую информацию с использованием сервиса ChatGPT через текстовый и голосовой ввод запросов.

Порядок работы:

1.	Заходим в Телеграмм и вводим название бота voice_text_GPT (или переходим по ссылке t.me/voice_text_GPT). 

2.	Для начала работы с ботом выбираем пункт меню /start. 

3.	Вводим произвольное текстовое сообщение. 
Появляется сообщение с ответом от ChatGPT.

4.	Отправляем голосовое сообщение. 
Появляется текстовое сообщение - преобразованное из голосового и сообщение с ответом от ChatGPT.

Этапы работы над проектом
1. Сбор требований и проектирование
- Определение функционала: Сбор требований от потенциальных пользователей, определение ключевых функций бота (текстовые и голосовые запросы, ответы от ChatGPT).
- Проектирование архитектуры: Разработка архитектуры бота, определение необходимых компонентов и взаимодействий между ними.

2. Настройка окружения
- Создание проекта: Настройка рабочего окружения для разработки бота (выбор языка программирования, фреймворка и библиотек).
- Регистрация бота в Telegram: Получение токена доступа для взаимодействия с API Telegram через BotFather.

3. Разработка функционала бота
- Обработка текстовых сообщений: Реализация логики обработки текстовых запросов пользователей и отправка их в ChatGPT для получения ответов.
- Обработка голосовых сообщений: Реализация функции распознавания речи для обработки голосовых команд и их конвертации в текст.
- Взаимодействие с ChatGPT: Создание меню пользователя и интеграция с API ChatGPT для отправки запросов и получения ответов.
