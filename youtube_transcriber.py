import csv
import json
import os
from timeit import default_timer as timer

import whisper
from pytube import YouTube
from tqdm import tqdm


def create_meta_table(video_name):
    """Создаёт метатаблицу в соответствии с вводом информации от пользователя в формате csv и json"""

    q = input("[INFO] Создать метаблицу для данного аудиофайла? да/нет: ")

    if q == "да" or "Да":

        all_data = []

        with open(f"downloaded_audio\{video_name}.csv", "w", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow(
                (
                    "Имя автора",
                    "Пол автора",
                    "Дата рождения автора",
                    "Название доклада/лекции",
                    "Место записи речи",
                    "Тип текста",
                    "Тематика текста",
                    "Дата создания текста",
                )
            )

        author_name = input("[INFO] Имя автора: ")
        author_sex = input("[INFO] Пол автора: ")
        author_birth = input("[INFO] Дата рождения автора: ")
        speech_name = input("[INFO] Название доклада/лекции: ")
        speech_place_name = input("[INFO] Место записи речи: ")
        speech_type = input("[INFO] Тип текста: ")
        speech_theme = input("[INFO] Тематика текста: ")
        speech_creation_date = input("[INFO] Дата создания текста: ")

        with open(f"downloaded_audio\{video_name}.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow(
                (
                    author_name,
                    author_sex,
                    author_birth,
                    speech_name,
                    speech_place_name,
                    speech_type,
                    speech_theme,
                    speech_creation_date,
                )
            )

        all_data.append(
            {
                video_name: (
                    {
                        "author_name": author_name,
                        "author_sex": author_sex,
                        "author_birth": author_birth,
                        "speech_name": speech_name,
                        "speech_place_name": speech_place_name,
                        "speech_type": speech_type,
                        "speech_theme": speech_theme,
                        "speech_creation_date": speech_creation_date,
                    }
                )
            }
        )

        with open(f"downloaded_audio\{video_name}.json", "w", encoding="utf-8") as file:
            json.dump(all_data, file, indent=4, ensure_ascii=False)
    else:
        pass


def download_audio():
    """Скачивает аудиофайл с YouTube по заданному url-адресу"""

    # определяем url видео
    video_urls = []
    url = input(f"\n[INFO] Вставьте ссылку на видео: ")
    video_urls.append(url)

    # указываем папку для сохранённых аудиофайлов и скачиваем файл
    destination = input(f"\n[INFO] Укажите полный путь сохранения аудиофайла: ")

    # проходимся по каждой ссылке из списка
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
            Продолжительность видео в секундах: {video_info.length}\n"""
        )  # дополнительная информация о видеоролике

        out_file = video.download(output_path=destination)

        # сохраняем
        base, ext = os.path.splitext(out_file)
        new_file = base + ".mp3"
        os.rename(out_file, new_file)

        # создаём метатаблицу в csv и json, передавая название аудиофайла
        create_meta_table(video_info.title)

        # выводим результат
        print(f"\n[INFO] <<{video_info.title}>> успешно скачан.\n")


def make_new_line(video_name):
    """Переносит каждое предложение в файле после точки, восклицательного или вопросительного знака на новую строку"""

    search_period = "."
    replace_period = ".\n"
    search_exclamation = "!"
    replace_exclamation = "!\n"
    search_question = "?"
    replace_question = "?\n"

    with open(video_name, "r", encoding="utf-8") as file:
        data = file.read()
        data = data.replace(search_period, replace_period)
        data = data.replace(search_exclamation, replace_exclamation)
        data = data.replace(search_question, replace_question)

    with open(video_name, "w", encoding="utf-8") as file:
        file.write(data)

    file.close()


def transcribe_audio():
    """Транскрибирует аудиофайл"""

    # выбираем модель Whisper
    model = whisper.load_model(
        input(
            f"\n[INFO] Укажите название модели (tiny, base, small, medium или large): "
        )
    )

    # определяем папку со скачанными файлами
    root_folder = input(f"\n[INFO] Укажите полный путь к скачанным файлам: ")

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
                    with open(
                        os.path.join(dirpath, filename_no_ext + ".txt"),
                        "w",
                        encoding="utf-8",
                    ) as f:
                        f.write(transcription)
                    pbar.update(1)

                    # q = input(
                    #     f"\n[INFO] Перенести каждое предложение после точки, восклицательного и вопросительного знака на новую строку? да/нет: "
                    # )
                    # if q == "да" or "Да":
                    #     make_new_line(filename_no_ext + ".txt")
                    # else:
                    #     pass


start_app_time = timer()  # отсчёт с начала работы программы

transcribe_audio()

overall_app_time = timer() - start_app_time  # общий подсчёт времени

print(
    f"\n[INFO] Работа завершена.\nОбщее время работы программы: {round(overall_app_time)} секунд(а).\n"
)
