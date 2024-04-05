import os
from timeit import default_timer as timer

import whisper
from pytube import YouTube
from tqdm import tqdm

start_app_time = timer()  # отсчёт с начала работы программы

# определяем url видео и скачиваем
video_urls = {
    "https://youtu.be/3Xu0j56dhBE",
}

for i, video_url in enumerate(video_urls):
    video_info = YouTube(video_url)
    print(i)
    print(f"\n[INFO] Скачиваю <<{video_info.title}>>\n")

    # берём из видеофайла только аудиодорожку
    video = YouTube(video_url).streams.filter(only_audio=True).first()
    print(
        f"""[INFO]
        Автор: {video_info.author}
        Дата загруки: {video_info.publish_date}
        Обложка: {video_info.thumbnail_url}
        Количество просмотров: {video_info.views}
        Продолжительность видео в секундах: {video_info.length}"""
    )  # дополнительная информация о видеоролике

    # указываем папку для сохранённых аудиофайлов и скачиваем файл
    destination = "D:\YandexDisk\Education\IT\Python\Learning Python\Python-YouTube-Transcriber\downloaded_audio"

    out_file = video.download(output_path=destination)

    # сохраняем
    base, ext = os.path.splitext(out_file)
    new_file = base + ".mp3"
    os.rename(out_file, new_file)

    # выводим результат
    print(f"\n[INFO] <<{video_info.title}>> успешно скачан.\n")


# определяем папку со скачанными файлами
root_folder = "D:\YandexDisk\Education\IT\Python\Learning Python\Python-YouTube-Transcriber\downloaded_audio"

model = whisper.load_model("large") # выбираем между medium и large

# определяем количество файлов в папке и в подпапках
num_files = sum(
    1
    for dirpath, dirnames, filenames in os.walk(root_folder)
    for filename in filenames
    if filename.endswith(".mp3")
)

# Транскрибируем файлы и выводим прогресс-бар
print(f"[INFO] Начинаю создание текста...\n")
with tqdm(total=num_files, desc="\n[INFO] Готовность текста") as pbar:
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(".mp3"):
                filepath = os.path.join(dirpath, filename)
                result = model.transcribe(filepath, fp16=False, verbose=True)
                transcription = result["text"]

                # Записываем информацию в текстовый файл
                filename_no_ext = os.path.splitext(filename)[0]
                with open(os.path.join(dirpath, filename_no_ext + ".txt"), "w") as f:
                    f.write(transcription)
                pbar.update(1)

overall_app_time = timer() - start_app_time  # общий подсчёт времени

print(f"\n[INFO] Работа завершена.\nОбщее время работы программы: {round(overall_app_time)} секунд(а).\n")
