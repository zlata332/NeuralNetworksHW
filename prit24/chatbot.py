from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from datetime import datetime
import requests


model_name = "sberbank-ai/rugpt3small_based_on_gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)


cities_kg = {
    "Бишкек": "Bishkek",
    "Ош": "Osh",
    "Джалал-Абад": "Jalal-Abad",
    "Каракол": "Karakol",
    "Токмок": "Tokmok",
    "Нарын": "Naryn",
    "Баткен": "Batken",
    "Талас": "Talas"
}


def get_weather(city_name):
    """Получает текущую температуру через OpenWeatherMap API"""
    api_key = "YOUR_API_KEY" 
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric&lang=ru"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("main"):
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            return f"Сейчас в {city_name} {temp:.1f}°C, {description}."
        else:
            return "Не удалось получить данные о погоде."
    except Exception as e:
        return f"Ошибка при получении погоды: {e}"

print('Чат-бот запущен. Для выхода напиши "выход".\n')


while True:
    user_input = input("Ты: ").strip().lower()
    if user_input in ['выход', 'exit']:
        print("Пока!")
        break


    if "время" in user_input:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"Бот: Сейчас {now}.")
        continue


    if "температур" in user_input or "погод" in user_input:
        found_city = None
        for ru_name, en_name in cities_kg.items():
            if ru_name.lower() in user_input:
                found_city = en_name
                break
        if found_city:
            print("Бот:", get_weather(found_city))
        else:
            print("Бот: Уточни, пожалуйста, город в Кыргызстане.")
        continue


    prompt = f"Ты — дружелюбный русскоязычный чат-бот. Общайся естественно.\nЧеловек: {user_input}\nБот:"
    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    output_ids = model.generate(
        input_ids,
        max_length=250,
        temperature=0.9,
        top_p=0.9,
        do_sample=True,
        repetition_penalty=1.2,
        pad_token_id=tokenizer.eos_token_id
    )

    response = tokenizer.decode(output_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
    print(f"Бот: {response.strip()}")
