# MiCloudAlbumDownloader

**MiCloudAlbumDownloader** is a Python script that allows you to download pictures or videos from Xiaomi Cloud album. It provides a convenient way to retrieve and save media files from your Xiaomi Cloud.

## Prerequisites

- Python 3.x
- requests library

## Installation

1. Clone or download the script to your local machine.
2. Install the requests library by running the following command:

   ```bash
   pip install requests
   ```

## Usage

1. Fill in the cookies of your Xiaomi Cloud album in the `cookies` parameter of the `MiCloudDownloader` class initialization.

   ```python
   MiCloudDownloader(cookies="your_cookies_here")
   ```

2. Customize the optional parameters according to your needs:

   - `album_id` (string): The ID of the album you want to download from (default: "1").
   - `start_date` (string): The start date of the photos you want to download (default: "20100101").
   - `end_date` (string): The end date of the photos you want to download (default: "20230101").
   - `pic_or_vid` (boolean): Set to `True` if you want to download only pictures, `False` if you want to download both pictures and videos (default: `True`).

## License

This project is licensed under the MIT License.
