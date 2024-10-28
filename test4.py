import requests

# Ваш токен бота от BotFather
TOKEN = "7779914668:AAEuMOeS7yCYKLaAAF6FRHW6ooBwJjTxfEc"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Вопросы и ответы
questions = [
    {
        "question": "Какой язык программирования мы используем?",
        "options": ["Python", "JavaScript", "C++", "Ruby"],
        "correct_option": 0
    },
    {
        "question": "Какой из этих языков используется для веб-разработки?",
        "options": ["Python", "C#", "JavaScript", "R"],
        "correct_option": 2
    }
]

# Переменные для отслеживания состояния пользователя
user_data = {}

def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

def start(chat_id):
    user_data[chat_id] = {"score": 0, "question_index": 0}
    ask_question(chat_id)

def ask_question(chat_id):
    question_index = user_data[chat_id]["question_index"]
    question_data = questions[question_index]
    question_text = question_data["question"]

    # Клавиатура с вариантами ответов
    keyboard = [
        [{"text": option, "callback_data": str(i)}] for i, option in enumerate(question_data["options"])
    ]
    reply_markup = {"inline_keyboard": keyboard}

    send_message(chat_id, question_text, reply_markup)

def handle_answer(chat_id, user_choice):
    question_index = user_data[chat_id]["question_index"]
    question_data = questions[question_index]
    correct_option = question_data["correct_option"]

    if user_choice == correct_option:
        send_message(chat_id, "Ваш ответ верный!")
        user_data[chat_id]["score"] += 1
    else:
        correct_answer = question_data["options"][correct_option]
        send_message(chat_id, f"Ваш ответ неверен. Правильный ответ: {correct_answer}")

    # Переход к следующему вопросу или окончание опроса
    if question_index + 1 < len(questions):
        user_data[chat_id]["question_index"] += 1
        ask_question(chat_id)
    else:
        score = user_data[chat_id]["score"]
        send_message(chat_id, f"Опрос завершен. Количество правильных ответов: {score}/{len(questions)}.")
        send_message(chat_id, "Хотите пройти опрос снова? Введите /start.")
        user_data[chat_id] = {"score": 0, "question_index": 0}

def process_update(update):
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        if update["message"]["text"] == "/start":
            start(chat_id)
    elif "callback_query" in update:
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        user_choice = int(update["callback_query"]["data"])
        handle_answer(chat_id, user_choice)

def main():
    offset = None
    while True:
        url = f"{BASE_URL}/getUpdates"
        params = {"timeout": 100, "offset": offset}
        response = requests.get(url, params=params)
        updates = response.json()["result"]

        for update in updates:
            process_update(update)
            offset = update["update_id"] + 1

if __name__ == '__main__':
    main()