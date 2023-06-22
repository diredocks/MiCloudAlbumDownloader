# MiCloudAlbumDownloader

**MiCloudAlbumDownloader** 是一个用于从小米云相册下载照片或视频的 Python 脚本。它提供了一种方便的方式来检索和保存小米云中的媒体文件。📸🎥

## 先决条件

- Python 3.x ✅
- requests 库 📚

## 安装

1. 克隆或下载脚本到您的本地机器。🖥️
2. 运行以下命令安装 requests 库： 💻

   ```bash
   pip install requests
   ```

## 使用方法

1. 在 `MiCloudDownloader` 类初始化中的 `cookies` 参数中填入您的小米云相册的 cookies。🍪

   ```python
   MiCloudDownloader(cookies="your_cookies_here")
   ```

2. 根据需求自定义可选参数：

   - `album_id`（字符串）：要下载的相册的 ID（默认为 "1"）。📷
   - `start_date`（字符串）：要下载的照片的起始日期（默认为 "20100101"）。📅
   - `end_date`（字符串）：要下载的照片的结束日期（默认为 "20230101"）。📅
   - `pic_or_vid`（布尔值）：如果只想下载图片，则设置为 `True`；如果只想下载视频，则设置为 `False`（默认为 `True`）。📽️
   - `path`（字符串）：要下载到的目录（默认为脚本当前目录）。💼

## 许可证

本项目使用 [MIT 许可证](LICENSE)。⚖️
