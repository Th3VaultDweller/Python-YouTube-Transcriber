from pytube import YouTube

# определяем url видео и скачиваем
video_url = input("Вставьте url-адрес видео, которое хотите скачать: ")
video_info = YouTube(video_url)
print(f"\n[INFO] Скачиваю видео <<{video_info.title}>>\n")

video_download = (
    YouTube(video_url)
    .streams.get_highest_resolution()
    .download(
        output_path="D:\YandexDisk\Education\IT\Python\Learning Python\Python-YouTube-Transcriber\downloaded_videos"
    )
)
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
