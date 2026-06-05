from groq import Groq
import google.generativeai as genai
from config import (
    GROQ_API_KEY, GEMINI_API_KEY,
    GROQ_FAST_MODEL, GROQ_SMART_MODEL, GEMINI_MODEL,
    SHORT_CONTEXT_LIMIT, MEDIUM_CONTEXT_LIMIT
)

groq_client = Groq(api_key=GROQ_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(GEMINI_MODEL)


def choose_model(context: str, question: str) -> str:
    total_length = len(context) + len(question)
    if total_length <= SHORT_CONTEXT_LIMIT:
        return "groq_fast"
    elif total_length <= MEDIUM_CONTEXT_LIMIT:
        return "groq_smart"
    else:
        return "gemini"


async def ask_groq(model: str, system: str, user_message: str) -> str:
    response = groq_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=2048
    )
    return response.choices[0].message.content


async def ask_gemini(system: str, user_message: str) -> str:
    prompt = f"{system}\n\n{user_message}"
    response = gemini_model.generate_content(prompt)
    return response.text


async def answer(question: str, context: str = "", sources: list[str] = None) -> tuple[str, str]:
    model_choice = choose_model(context, question)

    if context:
        sources_str = ", ".join(sources) if sources else "невідомо"
        system = (
            "Ти корисний асистент. Відповідай на питання користувача "
            "виключно на основі наданого контексту з його документів. "
            "Якщо відповіді немає в контексті — так і скажи. "
            f"Джерела: {sources_str}"
        )
        user_message = f"Контекст:\n{context}\n\nПитання: {question}"
    else:
        system = (
            "Ти корисний асистент. Відповідай чітко і по суті. "
            "Якщо питання стосується документів користувача але база порожня — "
            "порадь спочатку завантажити документи."
        )
        user_message = question

    if model_choice == "groq_fast":
        result = await ask_groq(GROQ_FAST_MODEL, system, user_message)
        model_name = f"Groq ({GROQ_FAST_MODEL})"
    elif model_choice == "groq_smart":
        result = await ask_groq(GROQ_SMART_MODEL, system, user_message)
        model_name = f"Groq ({GROQ_SMART_MODEL})"
    else:
        result = await ask_gemini(system, user_message)
        model_name = f"Gemini ({GEMINI_MODEL})"

    return result, model_name


async def summarize(text: str, instruction: str = "Зроби детальний конспект") -> tuple[str, str]:
    model_choice = choose_model(text, instruction)
    system = "Ти корисний асистент для роботи з документами. Відповідай українською якщо не вказано інше."
    user_message = f"{instruction}:\n\n{text}"
    
    if model_choice in ("groq_fast", "groq_smart"):
        if len(text) > SHORT_CONTEXT_LIMIT:
            model_choice = "groq_smart"
        result = await ask_groq(
            GROQ_FAST_MODEL if model_choice == "groq_fast" else GROQ_SMART_MODEL,
            system, user_message
        )
        model_name = f"Groq ({'fast' if model_choice == 'groq_fast' else 'smart'})"
    else:
        result = await ask_gemini(system, user_message)
        model_name = f"Gemini ({GEMINI_MODEL})"

    return result, model_name
