# utils/shortener.py
import aiohttp


async def shorten_url(api_url, api_key, long_url):
    """
    Shorten a URL using a generic shortener API.
    Format: https://shortener-domain/api?api=API_KEY&url=LONG_URL
    """
    try:
        full_url = f"{api_url}/api?api={api_key}&url={long_url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(full_url, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json(content_type=None)
                if data.get("status") == "success":
                    return data.get("shortenedUrl") or data.get("shortened_url")
                if "shortenedUrl" in data:
                    return data["shortenedUrl"]
                return None
    except Exception as e:
        print(f"Shortener error: {e}")
        return None
