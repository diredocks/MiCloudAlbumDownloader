import time
import json
import requests
from http.cookies import SimpleCookie


class MiCloudDownloader:
    """
    Xiaomi Cloud Album Downloader, which can download pictures or videos as needed.
    """

    def __init__(self, cookies, album_id="1", start_date="20100101", end_date="20230101", pic_or_vid=True):
        """
        Initialization function.

        :param cookies: Cookies of Xiaomi Cloud album, string type.
        :param album_id: Album ID, string type, default is "1".
        :param start_date: The start date of the photos you want to get, string type, default is "20100101".
        :param end_date: The end date of the photos you want to get, string type, default is "20230101".
        :param pic_or_vid: Whether to download only pictures, boolean type, default is True.
        """
        # Convert the cookies string to a dictionary type for later use.
        self.init_cookies = {k: v.value for k, v in SimpleCookie(cookies).items()}
        self.album_id = album_id
        self.start_date = start_date
        self.end_date = end_date
        self.pic_or_vid = pic_or_vid
        self.session = requests.Session()
        # Get the data required for the download link and establish the Session.
        self.initSession()
        self.mainLoop()

    def downloadFile(self, url, data, filename):
        """
        Download file.

        :param url: File download link, string type.
        :param data: Form data that needs to be submitted, string type.
        :param filename: The downloaded file name, string type.
        """
        with self.session.post(url, stream=True, data="meta=%s" % data) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                # Use streaming download to avoid reading the file into memory at once.
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded {filename}")

    def initSession(self):
        """Initialize session and get the data required for the download link."""
        self.session.get("https://i.mi.com/status/lite/setting?type=AutoRenewal&inactiveTime=10", cookies=self.init_cookies)
        print("Session initialized")

    def updateSession(self):
        """Update the session."""
        self.session.get("https://i.mi.com/status/lite/setting?type=AutoRenewal&inactiveTime=10")
        print("Session updated")

    def getDownloadInfo(self, pic_id):
        """
        Get the download link and form data required for the photo ID.

        :param pic_id: Photo ID, string type.
        """
        # Get the complete data required for the download link.
        download_info = self.session.get(f"https://i.mi.com/gallery/storage?id={pic_id}").json()["data"]["url"]
        download_info = self.session.get(download_info)
        # Convert JSONP format to JSON format.
        download_info = self.jsonpDump(download_info.text)
        return download_info

    def getPictures(self, page_num):
        """
        Get the photo information of the specified page number.

        :param page_num: The page number you want to get, string type.
        """
        pics_info = self.session.get(f"https://i.mi.com/gallery/user/galleries?&startDate={self.start_date}&endDate={self.end_date}&pageNum={page_num}&pageSize=30&albumId={self.album_id}").json()
        return pics_info["data"]

    def jsonpDump(self, jsonpStr):
        """
        Convert the JSONP format string to JSON format.

        :param jsonpStr: The string to be converted, string type.
        """
        # Construct the starting symbol and ending symbol of the JSONP string.
        _jsonp_begin = 'dl_img_cb('
        _jsonp_end = ')'
        jsonp_str = jsonpStr.strip()
        if not jsonp_str.startswith(_jsonp_begin) or not jsonp_str.endswith(_jsonp_end):
            raise ValueError('Invalid JSONP')
        # Get the string in the JSONP and parse it.
        return json.loads(jsonp_str[len(_jsonp_begin):-len(_jsonp_end)])

    def mainLoop(self):
        """The main loop function keeps getting photo information and downloading corresponding photos."""
        page_num = 0
        while True:
            pics_info = self.getPictures(str(page_num))
            print(f"Page {page_num}: {len(pics_info['galleries'])} pictures found")
            # Get all photos on each page.
            for pic_info in pics_info["galleries"]:
                # If only pictures are required, skip videos.
                if self.pic_or_vid and pic_info["type"] != "image":
                    continue
                # If only videos are required, skip pictures.
                if not self.pic_or_vid and pic_info["type"] == "image":
                    continue
                # Get the download link and form data required, and download the corresponding file.
                download_info = self.getDownloadInfo(pic_info["id"])
                self.downloadFile(download_info["url"], download_info["meta"], pic_info["fileName"])

            # End the loop if it has reached the last page.
            if pics_info["isLastPage"]:
                break

            page_num += 1
            # Wait for 1 second and update the Session.
            time.sleep(1)
            self.updateSession()
        print("All pictures are downloaded")


if __name__ == "__main__":
    MiCloudDownloader(cookies="")  # Fill in the cookies of Xiaomi Cloud album here.
