# utils/shortener.py
import aiohttp


async def shorten_url(api_url, api_key, long_url):
    try:
        api_url = api_url.rstrip("/")

        if not (api_url.startswith("http://") or api_url.startswith("https://")):
            api_url = "https://" + api_url

        full_url = f"{api_url}/api?api={api_key}&url={long_url}"
        print(f"DEBUG Shortener URL: {full_url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(full_url, timeout=15) as resp:
                if resp.status != 200:
                    print(f"Shortener HTTP error: {resp.status}")
                    return None

                data = await resp.json(content_type=None)
                print(f"DEBUG Shortener response: {data}")

                if isinstance(data, dict):
                    if data.get("status") == "success":
                        return data.get("shortenedUrl") or data.get("shortened_url")
                    if "shortenedUrl" in data:
                        return data["shortenedUrl"]
                    if "short" in data:
                        return data["short"]

                return None

    except Exception as e:
        print(f"Shortener error: {e}")
        return None
