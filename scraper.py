import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse


async def scrape_url(url: str) -> tuple[str, str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                raise ValueError(f"Сторінка повернула статус {resp.status}")
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string.strip() if soup.title else urlparse(url).netloc

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()

    main = (
        soup.find("article") or
        soup.find("main") or
        soup.find(id="content") or
        soup.find(class_="content") or
        soup.find("body")
    )

    if main:
        text = main.get_text(separator="\n", strip=True)
    else:
        text = soup.get_text(separator="\n", strip=True)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    return clean_text, title


def is_url(text: str) -> bool:
    try:
        result = urlparse(text.strip())
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False
