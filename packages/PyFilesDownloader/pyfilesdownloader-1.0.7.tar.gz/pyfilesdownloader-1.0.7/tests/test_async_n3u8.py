# coding: utf-8
import shutil

from PyFilesDownloader.async_loader.async_m3u8 import AsyncM3U8Downloader

url = 'https://v.cdnlz22.com/20250101/10507_73949974/index.m3u8'
# url = 'https://eyqygs.hhphxz.com/112-avid617e4e1e807f2.m3u8?300'
save_path = './download'
file_name = '【无码流出】小恶魔痴女大乱交.mp4'
loader = AsyncM3U8Downloader(url, save_path, file_name)
loader.run()


# print(shutil.which('ffmpeg'))