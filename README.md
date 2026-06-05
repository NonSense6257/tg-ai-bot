# AI Knowledge Base Bot

> Персональний Telegram-асистент з власною базою знань. Завантажуй документи — питай що завгодно.


## Можливості

- **PDF та TXT** — завантажуй файли будь-якого розміру
- **Посилання** — бот сам парсить статті та веб-сторінки
- **RAG** — відповіді базуються виключно на твоїх матеріалах
- **Авто-вибір моделі** — Groq або Gemini залежно від розміру контексту
- **Особиста база** — кожен користувач має окрему колекцію документів
- **Мінімум дій** — просто кидай файли або посилання, все інше бот робить сам


## Стек

| Технологія | Призначення |
|    ---     |     ---     |
| `aiogram 3` | Telegram Bot framework |
| `ChromaDB` | Векторна база даних |
| `Groq (Llama)` | Швидкі AI відповіді |
| `Gemini 1.5 Flash` | Великі документи, складний аналіз |
| `sentence-transformers` | Локальні embeddings |
| `PyMuPDF` | Читання PDF |
| `BeautifulSoup` | Парсинг веб-сторінок |


## Логіка вибору моделі

```
Розмір контексту < 2000 символів  →  Groq Llama 8B  (швидко)
Розмір контексту < 8000 символів  →  Groq Llama 70B (розумно)
Розмір контексту > 8000 символів  →  Gemini Flash   (великі документи)
```


## Структура проекту

```
tg-ai-bot/
├── bot.py          # Запуск бота
├── handlers.py     # Обробка повідомлень
├── ai.py           # AI логіка, вибір моделі
├── rag.py          # ChromaDB, RAG pipeline
├── scraper.py      # Парсинг посилань
├── config.py       # Конфігурація
├── requirements.txt
└── .env.example
```


## Запуск локально

### 1. Клонуй репозиторій
```bash
git clone https://github.com/NonSense6257/tg-ai-bot.git
cd tg-ai-bot
```

### 2. Створи віртуальне середовище
```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
```

### 3. Встанови залежності
```bash
pip install -r requirements.txt
```

### 4. Налаштуй токени
```bash
cp .env.example .env
nano .env
```

Заповни `.env`:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Запусти
```bash
python bot.py
```


## Де отримати токени

| Токен | Де отримати |
|  ---  |     ---     |
| `TELEGRAM_TOKEN` | [@BotFather](https://t.me/BotFather) в Telegram |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — безкоштовно |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) — безкоштовно |


## Команди бота

| Команда | Дія |
|---|---|
| `/start` | Привітання та інструкція |
| `/docs` | Список завантажених документів |
| `/delete [назва]` | Видалити документ |
| `/clear` | Очистити всю базу |
| `/help` | Допомога |


## Ліцензія

MIT License — дивись [LICENSE](LICENSE)
