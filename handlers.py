import os
import aiofiles
from aiogram import Router, F
from aiogram.types import Message, Document
from aiogram.filters import Command
from aiogram.utils.markdown import hbold, hcode

import rag
import ai
from scraper import scrape_url, is_url

router = Router()
DOWNLOADS_DIR = "./downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привіт, {hbold(message.from_user.first_name)}! 👋\n\n"
        "Я AI асистент з особистою базою знань.\n\n"
        "Що я вмію:\n"
        "📄 Приймати PDF та TXT файли\n"
        "🔗 Парсити сторінки за посиланням\n"
        "💬 Відповідати на питання по твоїх матеріалах\n"
        "🤖 Автоматично вибирати найкращу AI модель\n\n"
        "Просто кидай файли, посилання або питай що хочеш!\n\n"
        "Команди:\n"
        "/docs — список твоїх документів\n"
        "/clear — очистити всю базу\n"
        "/help — допомога",
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📚 <b>Як користуватись:</b>\n\n"
        "<b>Додати матеріали:</b>\n"
        "• Надішли PDF або TXT файл\n"
        "• Надішли посилання на статтю/сторінку\n\n"
        "<b>Питати:</b>\n"
        "• Просто напиши питання\n"
        "• Бот сам знайде відповідь у твоїх документах\n\n"
        "<b>Команди:</b>\n"
        "/docs — всі завантажені документи\n"
        "/clear — очистити всю базу знань\n"
        "/delete [назва] — видалити конкретний документ\n\n"
        "<b>Моделі (вибираються автоматично):</b>\n"
        "⚡ Groq Fast — короткі питання\n"
        "🧠 Groq Smart — середні задачі\n"
        "🔮 Gemini — великі документи, складний аналіз",
        parse_mode="HTML"
    )


@router.message(Command("docs"))
async def cmd_docs(message: Message):
    user_id = message.from_user.id
    docs = await rag.list_documents(user_id)

    if not docs:
        await message.answer("📭 База порожня. Надішли PDF, TXT або посилання!")
        return

    doc_list = "\n".join(f"• {d}" for d in docs)
    await message.answer(
        f"📚 <b>Твої документи ({len(docs)}):</b>\n\n{doc_list}",
        parse_mode="HTML"
    )


@router.message(Command("clear"))
async def cmd_clear(message: Message):
    user_id = message.from_user.id
    await rag.clear_all(user_id)
    await message.answer("🗑 База знань очищена.")


@router.message(Command("delete"))
async def cmd_delete(message: Message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("Вкажи назву документа: /delete назва")
        return

    source = args[1].strip()
    deleted = await rag.delete_document(user_id, source)

    if deleted:
        await message.answer(f"✅ Документ <b>{source}</b> видалено.", parse_mode="HTML")
    else:
        await message.answer(f"❌ Документ <b>{source}</b> не знайдено.", parse_mode="HTML")


@router.message(F.document)
async def handle_document(message: Message):
    user_id = message.from_user.id
    doc: Document = message.document
    file_name = doc.file_name or "document"
    ext = os.path.splitext(file_name)[1].lower()

    if ext not in (".pdf", ".txt"):
        await message.answer("⚠️ Підтримуються тільки PDF та TXT файли.")
        return

    status_msg = await message.answer(f"⏳ Обробляю <b>{file_name}</b>...", parse_mode="HTML")

    try:
        file_path = os.path.join(DOWNLOADS_DIR, f"{user_id}_{file_name}")
        file = await message.bot.get_file(doc.file_id)
        await message.bot.download_file(file.file_path, file_path)

        if ext == ".pdf":
            count = await rag.add_pdf(user_id, file_path, file_name)
        else:
            async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = await f.read()
            count = await rag.add_text(user_id, text, file_name)

        os.remove(file_path)

        await status_msg.edit_text(
            f"✅ <b>{file_name}</b> додано!\n"
            f"📊 Шматків збережено: {count}\n\n"
            "Тепер питай що завгодно про цей документ.",
            parse_mode="HTML"
        )

    except Exception as e:
        await status_msg.edit_text(f"❌ Помилка при обробці файлу: {e}")


@router.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if is_url(text):
        status_msg = await message.answer(f"⏳ Парсю сторінку...")
        try:
            content, title = await scrape_url(text)
            count = await rag.add_text(user_id, content, title)
            await status_msg.edit_text(
                f"✅ <b>{title}</b> додано!\n"
                f"📊 Шматків збережено: {count}\n\n"
                "Тепер питай що завгодно про цю сторінку.",
                parse_mode="HTML"
            )
        except Exception as e:
            await status_msg.edit_text(f"❌ Не вдалось завантажити сторінку: {e}")
        return

    status_msg = await message.answer("🤔 Думаю...")
    try:
        context, sources = await rag.query(user_id, text)
        response, model_name = await ai.answer(text, context, sources)

        sources_str = ""
        if sources:
            sources_str = "\n\n📚 <i>Джерела: " + ", ".join(sources) + "</i>"

        await status_msg.edit_text(
            f"{response}{sources_str}\n\n"
            f"<i>🤖 {model_name}</i>",
            parse_mode="HTML"
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Помилка: {e}")
