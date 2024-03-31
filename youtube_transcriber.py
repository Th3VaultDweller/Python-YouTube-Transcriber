import os
import time

import whisper
from pytube import YouTube

import downloaded_audio

# определяем url видео и скачиваем
video_urls = {
    "https://www.youtube.com/shorts/wt4Ct-aW6tQ?feature=share",
    "https://www.youtube.com/shorts/SMB1TsTJYjY?feature=share",
    "https://www.youtube.com/shorts/Fogu5ovZoDM?feature=share",
}

for i, video_url in enumerate(video_urls):
    video_info = YouTube(video_url)
    print(i)
    print(f"\n[INFO] Скачиваю <<{video_info.title}>>\n")

    video = YouTube(video_url).streams.filter(only_audio=True).first()
    print(
        f"""[INFO]
        Автор: {video_info.author}
        Дата загруки: {video_info.publish_date}
        Обложка: {video_info.thumbnail_url}
        Количество просмотров: {video_info.views}
        Продолжительность видео в секундах: {video_info.length}"""
    )

    # указываем папку для сохранённых аудиофайлов и скачиваем файл
    destination = "D:\YandexDisk\Education\IT\Python\Learning Python\Python-YouTube-Transcriber\downloaded_audio"

    out_file = video.download(output_path=destination)

    # сохраняем
    base, ext = os.path.splitext(out_file)
    new_file = base + ".mp3"
    os.rename(out_file, new_file)

    # выводим результат
    print(f"\n[INFO] <<{video_info.title}>> успешно скачан.\n")
