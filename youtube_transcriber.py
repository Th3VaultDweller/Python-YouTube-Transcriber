import os
import time

import whisper
from pytube import YouTube

# определяем url видео и скачиваем
video_url = input("Вставьте url-адрес видео: ")
video_info = YouTube(video_url)
print(f"\n[INFO] Скачиваю <<{video_info.title}>>\n")

video = YouTube(video_url).streams.filter(only_audio=True).first()
print(
    f"""[INFO]
      Автор: {video_info.author}
      Дата загруки: {video_info.publish_date}
      Описание: {video_info.description}
      Обложка: {video_info.thumbnail_url}
      Рейтинг видео: {video_info.rating}
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
print(video_info.title + " успешно скачан.")