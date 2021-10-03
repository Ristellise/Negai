import aiohttp
from mpegdash.parser import MPEGDASHParser
import aiofiles
import io


async def saveMemory(url, aioSession: aiohttp.ClientSession):
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en",
        "dnt": "1",
        "pragma": "no-cache",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/88.0.4324.190 Safari/537.36"
    }
    range_size = 9437184  # 9MB

    async with aioSession.get(url, headers=headers,
                              chunked=True) as request:
        if request.status == 200:
            with io.BytesIO() as f:
                print(f"Content length: {request.content_length}")
                e = await request.content.read()
                f.write(e)
                return f.getvalue()
        else:
            print(f"Error: {request.status}")
            return None


async def saveThread(url, aioSession: aiohttp.ClientSession, fileLocation):
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en",
        "dnt": "1",
        "pragma": "no-cache",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
    }
    range_size = 9437184  # 9MB
    downloaded = 0
    async with aiofiles.open(str(fileLocation), "wb") as f:
        while True:
            stop_pos = downloaded + range_size - 1
            headers_cl = headers.copy()
            headers_cl["range"] = f'bytes={downloaded}-{stop_pos}'

            response = await aioSession.get(url, headers=headers_cl)
            if response.status not in range(200, 299):
                print(f"Error while get: {response.status} {url[:256]}")
                return response.status
            # print(f"Status: {response.status}, {url}")
            chunk = await response.read()
            await f.write(chunk)
            if len(chunk) < range_size:
                if chunk == b"":
                    pass
                    # ?
                break
            downloaded += len(chunk)
        return str(fileLocation)


async def saveRaw(url, aioSession: aiohttp.ClientSession, fileLocation):
    print(url)

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en",
        "dnt": "1",
        "pragma": "no-cache",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
    }

    async with aioSession.get(url, headers=headers,
                              chunked=True) as request:
        if request.status == 200:
            async with aiofiles.open(str(fileLocation), "wb") as f:
                print(f"Content length: {request.content_length}")
                e = await request.content.read()
                await f.write(e)
            return str(fileLocation)
        else:
            print(f"Error: {request.status}")
            return None


async def saveDash(mpegUrl, aioSession: aiohttp.ClientSession, fileLocation):
    mpeg = MPEGDASHParser.parse(mpegUrl)
    for sets in mpeg.periods[0].adaptation_sets:
        if sets.mime_type == "audio/webm":
            for rep in sets.representations:
                base_url = rep.base_urls[0].base_url_value
                end = rep.segment_lists[0].segment_urls[-1].media.split("/")[-1].split("-")[-1]
                start = 0
                url = f"{base_url}range/{start}-{end}"
                print(url)
                return await saveRaw(url, aioSession, fileLocation)
