import requests, time, json
from http.cookies import SimpleCookie

class MiCloudDownloader:
    # album_id = 1 for camera roll, 2 for screenshots, get your album id on the mi cloud website
    # pic_or_vid = True means only download pictures, False means only download videos.
    def __init__(self, cookies, album_id="1", start_date="20100101", end_date="20230101", pic_or_vid=True):
        self.init_cookies = cookies
        self.album_id = album_id
        self.start_date = start_date
        self.end_date = end_date
        self.pic_or_vid = pic_or_vid
        self.cookiesDump()
        self.mainLoop()
        
    def cookiesDump(self):
        _cookies = SimpleCookie()
        _cookies.load(self.init_cookies)
        self.init_cookies = {k: v.value for k, v in _cookies.items()}

    def jsonpDump(self, jsonpStr):
        _jsonp_begin = r'dl_img_cb('
        _jsonp_end = r')'
        jsonp_str = jsonpStr.strip()
        if not jsonp_str.startswith(_jsonp_begin) or \
                not jsonp_str.endswith(_jsonp_end):
            raise ValueError('Invalid JSONP')
        return json.loads(jsonp_str[len(_jsonp_begin):-len(_jsonp_end)])

    def downloadFile(self, url, data, filename):
        with self.session.post(url, stream=True, data="meta=%s" % data) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)

    def initSession(self):
        self.session = requests.Session()
        self.session.get("https://i.mi.com/status/lite/setting?type=AutoRenewal&inactiveTime=10", cookies=self.init_cookies)

    def updateSession(self):
        self.session.get("https://i.mi.com/status/lite/setting?type=AutoRenewal&inactiveTime=10")

    def getDownloadInfo(self, pic_id):
        download_info = self.session.get("https://i.mi.com/gallery/storage?id=%s" % pic_id)
        download_info = download_info.json()["data"]["url"]
        download_info = self.session.get(download_info)
        download_info = self.jsonpDump(download_info.text)
        return download_info
    
    def getPictures(self, page_num):
        pics_info = self.session.get("https://i.mi.com/gallery/user/galleries?&startDate=%s&endDate=%s&pageNum=%s&pageSize=30&albumId=%s" % (self.start_date, self.end_date, str(page_num), self.album_id)).json()
        return pics_info["data"]
    
    def mainLoop(self):
        self.initSession()
        page_num = 0 # You can set the start num here.
        while True:
            pics_info = self.getPictures(str(page_num))
            page_num = page_num + 1
            # Get all the pictures
            for pic_info in pics_info["galleries"]:
                # Check the object type
                if self.pic_or_vid:
                    if pic_info["type"] != "image":
                        continue
                else:
                    if pic_info["type"] == "image":
                        continue
                # Get Download link and data to post
                download_info = self.getDownloadInfo(pic_info["id"])
                self.downloadFile(download_info["url"], download_info["meta"], pic_info["fileName"])
            # Check if it's the last page
            if pics_info["isLastPage"]:
                break
            # Chilling for a while~
            time.sleep(1)
            self.updateSession()

if __name__ == "__main__":
    MiCloudDownloader("") # Paste your cookie right here and enjoy it!
