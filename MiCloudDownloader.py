import os
import time
import json
import requests
from http.cookies import SimpleCookie


class MiCloudDownloader:
    """
    小米云相册下载器，可按需下载图片或视频。
    """

    def __init__(self, cookies, album_id="1", start_date="20100101", end_date="20230101", pic_or_vid=True, path=os.path.dirname(os.path.abspath(__file__))):
        """
        初始化函数。

        :param cookies: 小米云相册的cookies，字符串类型。
        :param path: 下载文件的路径，字符串类型，默认为空。
        :param album_id: 相册ID，字符串类型，默认为"1"。
        :param start_date: 想要获取照片的起始日期，字符串类型，默认为"20100101"。
        :param end_date: 想要获取照片的结束日期，字符串类型，默认为"20230101"。
        :param pic_or_vid: 是否只下载图片，布尔类型，默认为True。
        """
        # 将cookies字符串转换为字典类型以供后续使用。
        self.init_cookies = {k: v.value for k, v in SimpleCookie(cookies).items()}
        self.path = path
        self.album_id = album_id
        self.start_date = start_date
        self.end_date = end_date
        self.pic_or_vid = pic_or_vid
        self.session = requests.Session()
        # 判断目标目录是否存在，若不存在则提示用户
        if not os.path.exists(path):
            print(f"目录 \"{path}\" 不存在，请检查后手动创建该目录 ❌")
        # 获取下载链接所需的数据并建立Session。
        self.initSession()
        self.mainLoop()

    def downloadFile(self, url, data, filename):
        """
        下载文件。

        :param url: 文件下载链接，字符串类型。
        :param data: 需要提交的表单数据，字符串类型。
        :param filename: 下载的文件名，字符串类型。
        """

        # 拼接下载文件的完整路径
        filepath = os.path.join(self.path, filename)

        with self.session.post(url, stream=True, data="meta=%s" % data) as r:
            if r.status_code != 200:
                print(f"下载\"{filename}\"时出错 ❌")
                return

            r.raise_for_status()
            file_size = int(r.headers['Content-Length'])
            downloaded_size = 0

            with open(filepath, 'wb') as f:
                chunk_size = 8192
                kb_size = 1024
                mb_size = kb_size * kb_size
                
                print(f"\n开始下载\"{filename}\" 📥")

                # 使用流式下载，避免一次性将文件读入内存。
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 根据文件大小选择单位，并显示下载进度
                        if file_size >= mb_size:
                            progress = min(int((downloaded_size / file_size) * 100), 100)
                            units = "MB"
                        else:
                            progress = min(int((downloaded_size / file_size) * 100), 100)
                            units = "KB"
                        
                        print(f"下载进度：{progress}% {downloaded_size // kb_size}{units}/{file_size // kb_size}KB", end='\r', flush=True)

            print(f"\n已下载\"{filename}\" 🟢")

    def initSession(self):
        """初始化会话并获取下载链接所需的数据。"""
        try:
            self.session.get("https://i.mi.com/status/lite/setting?type=AutoRenewal&inactiveTime=10", cookies=self.init_cookies)
            print("会话已初始化 😌")  # 笑脸表情
        except requests.exceptions.RequestException as e:
            print(f"在会话初始化期间出现错误：{str(e)} ❌")  # 错误表情

    def updateSession(self):
        """更新会话。"""
        try:
            self.session.get("https://i.mi.com/status/lite/setting?type=AutoRenewal&inactiveTime=10")
            print("会话已更新 🙌")  # 举手表情
        except requests.exceptions.RequestException as e:
            print(f"在会话更新期间出现错误：{str(e)} ❌")  # 错误表情

    def getDownloadInfo(self, pic_id):
        """
        获取照片ID所需的下载链接和表单数据。

        :param pic_id: 照片ID，字符串类型。
        """
        try:
            # 获取下载链接所需的完整数据。
            download_info = self.session.get(f"https://i.mi.com/gallery/storage?id={pic_id}").json()["data"]["url"]
            download_info = self.session.get(download_info)
            # 将JSONP格式转换为JSON格式。
            download_info = self.jsonpDump(download_info.text)
            return download_info
        except (KeyError, requests.exceptions.RequestException) as e:
            print(f"在获取照片{pic_id}的下载信息时发生错误：{str(e)} ❌")  # 错误表情
            return None

    def getPictures(self, page_num):
        """
        获取指定页数的照片信息。

        :param page_num: 想要获取的页数，字符串类型。
        """
        try:
            pics_info = self.session.get(f"https://i.mi.com/gallery/user/galleries?&startDate={self.start_date}&endDate={self.end_date}&pageNum={page_num}&pageSize=30&albumId={self.album_id}").json()
            return pics_info["data"]
        except (KeyError, requests.exceptions.RequestException) as e:
            print(f"在从第{page_num}页获取照片时发生错误：{str(e)} ❌")  # 错误表情
            return None

    def jsonpDump(self, jsonpStr):
        """
        将JSONP格式的字符串转换为JSON格式。

        :param jsonpStr: 需要转换的字符串，字符串类型。
        """
        # 构造JSONP字符串的起始符号和结束符号。
        _jsonp_begin = 'dl_img_cb('
        _jsonp_end = ')'
        jsonp_str = jsonpStr.strip()
        if not jsonp_str.startswith(_jsonp_begin) or not jsonp_str.endswith(_jsonp_end):
            raise ValueError('无效的JSONP')
        # 获取JSONP中的字符串并解析。
        return json.loads(jsonp_str[len(_jsonp_begin):-len(_jsonp_end)])

    def mainLoop(self):
        """主循环函数，持续获取照片信息并下载相应的照片。"""
        page_num = 0
        while True:
            pics_info = self.getPictures(str(page_num))
            if not pics_info:
                break
            print(f"第{page_num}页：找到{len(pics_info['galleries'])}张照片 📷")  # 相机表情
            # 获取每一页上的所有照片。
            for pic_info in pics_info["galleries"]:
                # 如果只需要图片，则跳过视频。
                if self.pic_or_vid and pic_info["type"] != "image":
                    continue
                # 如果只需要视频，则跳过图片。
                if not self.pic_or_vid and pic_info["type"] == "image":
                    continue
                
                download_info = self.getDownloadInfo(pic_info["id"])
                if not download_info:
                    continue
                
                self.downloadFile(download_info["url"], download_info["meta"], pic_info["fileName"])

            # 如果已经到达最后一页，则结束循环。
            if pics_info["isLastPage"]:
                break

            page_num += 1
            # 等待1秒并更新会话。
            time.sleep(1)
            self.updateSession()
        print("\n所有照片已下载完成 🎉")  # 庆祝表情


if __name__ == "__main__":
    MiCloudDownloader()  # 在这里填入小米云相册的cookies。
