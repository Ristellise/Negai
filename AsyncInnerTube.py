"""
AsyncInnerTubery:

Async InnerTube Library for python.

"""
import collections.abc
import json
import logging
import math
import urllib.parse

import aiohttp
from protox import Message, String, Int32

from Negai import fsDownloader, utils


def rup(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = rup(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class InnerTubeException(Exception):
    pass


class InnerTubeVideo:
    """
    Container to define a Youtube video.
    """
    def __init__(self, **kwargs):
        """

        :param kwargs:
        """
        self.title = kwargs.get("title")
        self.videoId = kwargs.get("videoId")
        self.thumbnails = kwargs.get("thumbnails", {})
        self.thumbnails = sorted(self.thumbnails, key=lambda k: int(k['width']), reverse=True)
        self.channel = kwargs.get("channel", {})
        self.description = kwargs.get("description")
        if not isinstance(kwargs.get("duration", 0), float):
            raise InnerTubeException("Duration is not a float")
        else:
            self.duration = kwargs.get("duration", 0.0)
        if kwargs.get("streamingData"):
            self.buckets = self.fmt_responses(kwargs.get("streamingData"))

    @classmethod
    def fmt_responses(cls, streamingData: dict):
        """
        Converts streamingData into dictionaries called buckets.
        :param streamingData:
        :return:
        """
        buckets = {}
        for k, v in streamingData.items():
            if isinstance(v, list):
                for fmt in v:
                    itag_bucket = math.floor(fmt.get('itag', 0) / 100)
                    bucket = buckets.get(itag_bucket, {})
                    print(fmt)
                    mime = fmt.get("mimeType")
                    if "video/" in mime and "audio/" in mime:
                        stream_type = "mixed"
                    elif "video/" in mime:
                        stream_type = "video"
                    elif "audio/" in mime:
                        stream_type = "audio"
                    else:
                        stream_type = "unknown"
                    if fmt.get("audioQuality") is not None and any([stream_type == "mixed", stream_type == "audio"]):
                        quality = fmt.get("audioQuality")
                    else:
                        quality = fmt.get("quality")
                    bucket[fmt.get('itag', 0)] = {
                        "url": fmt.get("url"),
                        "type": stream_type,
                        "bitrate": fmt.get("bitrate"),
                        "contentLength": fmt.get("contentLength"),
                        "mimeType": mime,
                        "quality": quality
                    }
                    buckets[itag_bucket] = bucket
        return buckets

    @classmethod
    def from_player(cls, player: dict):
        """
        Converts a "player" endpoint to
        :param player:
        :return:
        """
        title = player["videoDetails"]["title"]
        videoId = player["videoDetails"]["videoId"]
        duration = float(player["videoDetails"]["lengthSeconds"])
        print(player["videoDetails"]["thumbnail"]["thumbnails"])
        thumbs = sorted(player["videoDetails"]["thumbnail"]["thumbnails"], key=lambda k: int(k['width']),
                        reverse=True)
        name_channel = player["videoDetails"]["author"]
        url_channel = f"https://youtube.com/channel/{player['videoDetails']['channelId']}"
        shortDescription = player["videoDetails"]["shortDescription"]
        cls(title=title, videoId=videoId, duration=duration, thumbnails=thumbs,
            channel={"name": name_channel, "url": url_channel},
            description=shortDescription)

    @classmethod
    async def download(cls, fileLocation, bucket: dict, itag_preference):
        itag_raw = {}
        for v in bucket.values():
            for k, v2 in v.items():
                itag_raw[k] = v2
        if isinstance(itag_preference, list):
            for itag in itag_preference:
                it = itag_raw.get(itag)
                if it is not None:
                    async with aiohttp.ClientSession() as session:
                        return await fsDownloader.saveThread(it['url'], session, fileLocation)


class InnerTube:
    """
    InnerTube Class
    """

    INNERTUBE_BASE = "https://www.youtube.com/youtubei"
    INNERTUBE_VERSION = "v1"

    SESSION: aiohttp.ClientSession = None
    LOGGER: logging.Logger = logging.getLogger("AsyncInnerTube")

    def __init__(self, aiohttpHttpConnector) -> None:
        pass

    @property
    def getInnerTube(self):
        return f"{self.INNERTUBE_BASE}/{self.INNERTUBE_VERSION}/"

    async def player(self, videoId: str, clientName: str = "ANDROID"):
        """
        Gets video streams and the video info.
        Uses android client name by default as it doesn't have any signature checks as it does for web.
        
        >>> TeamNewPipe:
            * The cipher signatures from the player endpoint without a signatureTimestamp are invalid.
            * So if the content is protected by signatureCiphers and if signatureTimestamp is not known,
            * we need to fetch again the desktop InnerTube API.
        >>> 
        
        Args:
            videoId ([type]): [description]
            clientName (str, optional): Defines the clientName to be accessed. Defaults to "ANDROID" as android does not have any signatureCipher Requirements.
        """
        payload = {"contentCheckOk": False,
                   "racyCheckOk": False,
                   "videoId": videoId,
                   "context": {"user": {"lockedSafetyMode": False}}
                   }
        clientName = clientName.upper()
        if clientName.startswith("WEB"):
            payload["playbackContext"] = {"contentPlaybackContext": {"signatureTimestamp": 18879}}
        response = await self.postRequest("player",
                                          clientName,
                                          payload)
        return response

    @classmethod
    def retrieve_video(cls, player_data: dict):
        """
        Unwraps player data into a dict which can is common to search.
        :param player_data:
        :return:
        """

        return InnerTubeVideo.from_player(player_data)

    @property
    async def JSCode(self):
        watchId = "dQw4w9WgXcQ"
        return None

    async def retrieveJS(self, videoId=None):
        """
        Retrieves the JS Code.
        There are 2 ways to retrieve JS Code:
         1. use: https://www.youtube.com/iframe_api. Extracting the hash pattern via regex [Cheap]
         2. using a known videoId that requires JSRetrival (Provided in opts) and try to get the JS from there. [Slower, but more reliable]
        
        This should only be called once. The JS Code will be cached and stored while the signatureTimestamp is to be extracted.
        (RE Thanks to TeamNewPipe)
        
        Args:
            videoId (str): The videoId as referance.
        """
        session = await self.getSession
        resp = await session.get("https://www.youtube.com/iframe_api")
        # if resp.status == 200 and

    async def browse(self, query, min_results=1):

        class baka(Message):
            hide_things: int = Int32(number=1, default=0)

        class params(Message):
            channel_tabs: str = String(number=2, required=False)
            response_display: baka = baka.as_field(number=104, required=False)

    async def pytube_uncyper(self, streamingData):
        """
        Gets the true urls from signature.
        This is mainly taken fdrom https://github.com/pytube/pytube/blob/master/pytube/__main__.py#L160.
        Args:
            streamingData ([type]): [description]
        """

    async def search(self, query, min_results=1):

        async def do_query(continuation: str = None):
            if continuation:
                resp = await self.postRequest("search", "WEB", {"continuation": continuation})
            else:
                resp = await self.postRequest("search", "WEB", {"query": query})
            return resp

        def runsExtrator(runs_list: list):
            return [i['text'] for i in runs_list]

        def extractItemSectionRender(bleh: dict):
            items = []
            for render in bleh.get("contents", []):

                k = list(render.keys())[0].lower()
                if "videorender" in k:
                    v = list(render.values())[0]
                    if "LIVE_NOW" in v.get('badges', [{}])[0].get('metadataBadgeRenderer', {}).get("style", ""):
                        continue
                    videoId = v['videoId']
                    thumbs = sorted(v["thumbnail"]["thumbnails"], key=lambda k2: int(k2['width']), reverse=True)
                    title = " ".join(runsExtrator(v["title"]["runs"]))
                    if v.get("lengthText") is None:
                        duration = 0.0
                    else:
                        duration = float(utils.unpack_HHMMSS(v["lengthText"]["simpleText"]))
                    channel = " ".join(runsExtrator(v["ownerText"]["runs"]))
                    items.append({"title": title,
                                  "videoId": videoId,
                                  "thumbs": thumbs,
                                  "duration": duration,
                                  "channel": channel})
                else:
                    continue
            return items

        def extract_response(jsonResponse: dict, isContinuation=False):
            if not isContinuation:
                contents = jsonResponse.get("contents", {}) \
                    .get('twoColumnSearchResultsRenderer', {}) \
                    .get('primaryContents', {}) \
                    .get('sectionListRenderer', {}).get("contents", [])
            else:
                contents = jsonResponse.get("onResponseReceivedCommands", [])[0] \
                    .get('appendContinuationItemsAction', {}).get("continuationItems", [])
            videos = None
            cont = None
            for c in contents:
                k = list(c.keys())[0]
                v = list(c.values())[0]
                if "continuation" in k.lower():
                    cont = v["continuationEndpoint"]["continuationCommand"]["token"]
                elif "sectionrender" in k.lower():
                    videos = extractItemSectionRender(v)
            return cont, videos

        c_results = 0
        cont = None
        videos = []
        while c_results < min_results:
            print(c_results, min_results)
            r = await do_query(continuation=cont)
            if r.status != 200:
                break
            rj = await r.json()
            cont, c_v = extract_response(rj, cont is not None)
            print(c_v)
            videos.extend(c_v)
            c_results = len(videos)
        return videos

    async def postRequest(self, innertube_route, clientName, payload=None, needsInnerKey=True):
        # Grab Headers & Client Context
        if payload is None:
            payload = {}
        headers, client_context, extra = self.createHeaders(clientName)

        # URL & Context Setup
        enc = urllib.parse.urlencode({"key": extra["innertube_key"]})
        url = f"{self.getInnerTube}{innertube_route}{'' if not needsInnerKey else '?' + enc}"
        compiled = rup(payload, {"context": {"client": client_context}})

        # Requests
        print(f"Fetch: {url}: {compiled}")
        session = await self.getSession
        response = await session.post(f"{url}",
                                      data=json.dumps(compiled),
                                      headers=headers)
        if response.status != 200:
            self.LOGGER.error(f"Response returned: {response.status}")
        return response

    # Client Sessions functions.

    @classmethod
    def createHeaders(cls,
                      clientName: str,
                      locale="en",
                      country="US"):
        ctx, ex = cls.createClientContext(clientName)
        if clientName.upper().startswith("WEB"):
            headers = {
                "accept": "*/*",
                "origin": "https://www.youtube.com",
                "referer": "https://www.youtube.com",
                "X-YouTube-Client-Name": str(ex["clientId"]),
                "X-YouTube-Client-Version": str(ctx["clientVersion"]),
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
            }
        elif clientName.upper().startswith("ANDROID"):
            # todo lol. 
            headers = {
                "accept": "*/*",
                "origin": "https://www.youtube.com",
                "referer": "https://www.youtube.com",
                "X-YouTube-Client-Name": str(ex["clientId"]),
                "X-YouTube-Client-Version": str(ctx["clientVersion"]),
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
            }
        else:
            raise InnerTubeException(f"Unknown clientName: {clientName}")
        return headers, ctx, ex

    @classmethod
    def createClientContext(cls,
                            clientName: str,
                            locale="en",
                            country="US"):
        cli = {
            "hl": locale,
            "gl": country,
            "clientName": None,
            "clientVersion": None
        }
        ex = {
            "clientId": -1,
            "innertube_key": None,
            "needs_js": True}
        clientName = clientName.upper()
        if clientName == "WEB":
            cli["clientName"] = clientName
            cli["clientVersion"] = '2.20210622.10.00'
            ex["clientId"] = 1
            ex["innertube_key"] = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
        elif clientName == "WEB_EMBEDDED_PLAYER":
            cli["clientName"] = clientName
            cli["clientVersion"] = '1.20210620.0.1'
            ex["clientId"] = 56
            ex["innertube_key"] = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
        elif clientName == "WEB_MUSIC" or clientName == "WEB_REMIX":
            cli["clientName"] = "WEB_REMIX"
            cli["clientVersion"] = '1.20210621.00.00'
            ex["clientId"] = 67
            ex["innertube_key"] = "AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30"
        # elif clientName == "WEB_CREATOR":
        #     cli["clientName"] = clientName
        #     cli["clientVersion"] = '1.20210621.00.00'
        #     ex["clientId"] = 62
        elif clientName == "ANDROID":
            cli["clientName"] = clientName
            cli["clientVersion"] = '16.20'
            ex["clientId"] = 3
            ex["innertube_key"] = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
            ex["needs_js"] = False
        elif clientName == "ANDROID_EMBEDDED_PLAYER":
            cli["clientName"] = clientName
            cli["clientVersion"] = '16.20'
            ex["clientId"] = 55
            ex["innertube_key"] = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
            ex["needs_js"] = False
        # elif clientName == "ANDROID_MUSIC":
        #     cli["clientName"] = clientName
        #     cli["clientVersion"] = '4.32'
        #     ex["clientId"] = 21
        # elif clientName == "ANDROID_CREATOR":
        #     cli["clientName"] = clientName
        #     cli["clientVersion"] = '21.24.100'
        #     ex["clientId"] = 14
        if not ex["innertube_key"] or not ex["clientId"] or not cli["clientName"] or not cli["clientVersion"]:
            raise InnerTubeException("Missing Key, clientId, clientName or clientVersion")
        return cli, ex

    @property
    async def getSession(self):
        if not self.SESSION:
            self.SESSION = aiohttp.ClientSession()
        return self.SESSION
