import csv
import json
import os
from timeit import default_timer as timer

import nltk
import pandas as pd
import pymorphy2
import whisper
from nltk.tokenize import sent_tokenize, word_tokenize
from pytube import YouTube
from tqdm import tqdm

nltk.download("punkt")


def create_meta_table(video_name):
    """Создаёт метатаблицу в формате csv и json в соответствии с вводом информации от пользователя"""

    q = input("[INFO] Создать метаблицу для данного аудиофайла? да/нет: ")

    if q == "Да" or "да":

        all_data = []  # создаём список для последующего заполнения json-файла

        # создаём csv-таблицу
        with open(
            f"downloaded_audio\{video_name}\{video_name}.csv", "w", encoding="utf-8"
        ) as file:
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

        # указываем необходимую информацию об аудиофайле
        speaker_name = input("[INFO] Имя автора: ")
        speaker_sex = input("[INFO] Пол автора: ")
        speaker_birth = input("[INFO] Дата рождения автора: ")
        speech_name = input("[INFO] Название доклада/лекции: ")
        speech_place_name = input("[INFO] Место записи речи: ")
        speech_type = input("[INFO] Тип текста: ")
        speech_theme = input("[INFO] Тематика текста: ")
        speech_creation_date = input("[INFO] Дата создания текста: ")

        # заполняем csv-таблицу
        with open(
            f"downloaded_audio\{video_name}\{video_name}.csv", "a", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)

            writer.writerow(
                (
                    speaker_name,
                    speaker_sex,
                    speaker_birth,
                    speech_name,
                    speech_place_name,
                    speech_type,
                    speech_theme,
                    speech_creation_date,
                )
            )

        # заполняем список all_data
        all_data.append(
            {
                video_name: (
                    {
                        "speaker_name": speaker_name,
                        "speaker_sex": speaker_sex,
                        "speaker_birth": speaker_birth,
                        "speech_name": speech_name,
                        "speech_place_name": speech_place_name,
                        "speech_type": speech_type,
                        "speech_theme": speech_theme,
                        "speech_creation_date": speech_creation_date,
                    }
                )
            }
        )

        # и сохраняем как json-файл
        with open(
            f"downloaded_audio\{video_name}\{video_name}.json", "w", encoding="utf-8"
        ) as file:
            json.dump(all_data, file, indent=4, ensure_ascii=False)

    else:
        pass


def download_audio():
    """Скачивает аудиофайл с YouTube по заданному url-адресу"""

    # определяем url видео
    url_input = input(
        f"\n[INFO] Вставьте ссылку на видео или несколько ссылок через пробел: "
    )
    video_urls = url_input.split()  # создаёт список из url-адресов

    # проходимся по каждой ссылке из списка и выводим прогресс-бар
    for i, video_url in enumerate(tqdm(video_urls, total=len(video_urls))):
        video_info = YouTube(video_url)
        print(i)
        print(f"\n[INFO] Скачиваю <<{video_info.title}>>\n")

        character_to_find = "|"
        character_to_replace = "-"
        if character_to_find in video_info.title:
            video_info.title.replace(character_to_find, character_to_replace)

        # указываем папку для сохранённых аудиофайлов и скачиваем файл
        try:
            print("[INFO] Создаю директорию для сохранения файлов...\n")
            os.mkdir(f"./downloaded_audio/{video_info.title}")
        except OSError as error:
            print("[INFO] Директория уже существует.\n")
            pass

        # берём из видеофайла только аудиодорожку
        video = YouTube(video_url).streams.filter(only_audio=True).first()
        print(
            f"""[INFO]
            Автор: {video_info.author}
            Дата загруки: {video_info.publish_date}
            Обложка: {video_info.thumbnail_url}
            Количество просмотров: {video_info.views}
            Продолжительность видео в секундах: {video_info.length}
            Источник: {video_url}\n"""
        )  # дополнительная информация о видеоролике

        out_file = video.download(output_path=f"downloaded_audio/{video_info.title}")

        # сохраняем
        try:
            base, ext = os.path.splitext(out_file)
            new_file = base + ".mp3"
            os.rename(out_file, new_file)
        except FileExistsError:
            print(f"[INFO] Файл {video_info.title}.mp3 уже существует.")

        # выводим результат
        print(f"\n[INFO] <<{video_info.title}>> успешно скачан.\n")

        # создаём метатаблицу в csv и json, передавая название аудиофайла
        create_meta_table(video_info.title)


def make_new_line(video_name):
    """Переносит каждое предложение в файле после точки, восклицательного или вопросительного знака на новую строку"""

    # определяем необходимые знаки для поиска и замены
    search_period = "."
    replace_period = ".\n"
    search_exclamation = "!"
    replace_exclamation = "!\n"
    search_question = "?"
    replace_question = "?\n"

    # заменяем ранее обозначенные знаки
    with open(video_name, "r", encoding="utf-8") as file:
        data = file.read()
        data = data.replace(search_period, replace_period)
        data = data.replace(search_exclamation, replace_exclamation)
        data = data.replace(search_question, replace_question)

    # сохраняем
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
    try:
        root_folder = "downloaded_audio"
    except:
        root_folder = input(
            "[INFO] Укажите директорию для аудиофайлов для транскрибирования: "
        )

    # определяем количество файлов в папке и в подпапках
    num_files = sum(
        1
        for dirpath, dirnames, filenames in os.walk(root_folder)
        for filename in filenames
        if filename.endswith(".mp3")
    )

    # транскрибируем файлы и выводим прогресс-бар
    print(f"\n[INFO] Начинаю создание текста...\n")
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

                    # делаем разделение на отдельные строки, если есть необходимость
                    q = input(
                        f"\n[INFO] Перенести каждое предложение после точки, восклицательного и вопросительного знака на новую строку? да/нет: "
                    )
                    if q == "да" or "Да":
                        try:
                            make_new_line(
                                f"{root_folder}/{filename_no_ext}/{filename_no_ext}"
                                + ".txt"
                            )
                        except FileNotFoundError:
                            print(
                                f"\n[INFO] Файл не найден в директории (FileNotFoundError)."
                            )
                            pass
                    else:
                        pass


def make_alignment(video_name):
    """Сегментирует текст на слова/токены и предложения"""

    with open(video_name, "r", encoding="utf-8") as file:
        text = file.read()
        string = text.replace("\n", " ")
        tokenized_text = word_tokenize(text)
        sent_text = sent_tokenize(text)
        print(tokenized_text[0:5])
        print(sent_text[0:5])

        tokenized_sent = []
        for sent in sent_text:
            tokenized_sent.append(word_tokenize(sent))
            # print(tokenized_sent)

    alignments_list = [[] for x in range(len(sent_text))]
    pos_list = [[] for x in range(len(sent_text))]

    # проверяем длину списков
    print(
        f"\n[INFO] Длина списка разметок: {len(alignments_list)},\n[INFO] Длина списка частей речи: {len(pos_list)}"
    )

    morph = pymorphy2.MorphAnalyzer()

    for i in range(len(tokenized_sent)):
        for j in range(len(tokenized_sent[i])):
            alignments_list[i].append(morph.parse(tokenized_sent[i][j]))
    # print(tokenized_sent[0])
    # print(alignments_list[0])

    probable_alignment = [[] for x in range(len(alignments_list))]
    # print(len(probable_alignment))

    for i in range(len(alignments_list)):
        for j in range(len(alignments_list[i])):
            probable_alignment[i].append(alignments_list[i][j][0])
    # print(probable_alignment[0])

    tags = [[] for x in range(len(probable_alignment))]
    lemmas = [[] for x in range(len(probable_alignment))]
    pos = [[] for x in range(len(probable_alignment))]
    for i in range(len(probable_alignment)):
        for j in range(len(probable_alignment[i])):
            tags[i].append(probable_alignment[i][j].tag)
            lemmas[i].append(probable_alignment[i][j].normal_form)
            pos[i].append(probable_alignment[i][j].tag.POS)

    text_data_per_sent = pd.DataFrame(
        data={
            "Предложение": sent_text,
            "Словоформа": tokenized_sent,
            "Варианты разметки": alignments_list,
            "Вероятная разметка": probable_alignment,
            "Часть речи": pos,
            "Лемма": lemmas,
            "Тэги": tags,
        }
    )

    text_data_per_sent.head()

    sent_list_for_index = []
    for i in range(len(tokenized_sent)):
        for j in range(len(tokenized_sent[i])):
            sent_list_for_index.append(sent_text[i])

    alignments_list_full = []
    pos_list_full = []
    for word in tokenized_text:
        alignments_list_full.append(morph.parse(word))
        pos_list_full.append(morph.parse(word)[0].tag.POS)

    probable_alignment_full = [i[0] for i in alignments_list_full]

    tags_full = []
    lemmas_full = []
    pos_full = []
    for alignment in probable_alignment_full:
        tags_full.append(alignment.tag)
        lemmas_full.append(alignment.normal_form)
        pos_full.append(alignment.tag.POS)

    text_data = pd.DataFrame(
        data={
            "Предложение": sent_list_for_index,
            "Словоформа": tokenized_text,
            "Варианты разметки": alignments_list_full,
            "Вероятная разметка": probable_alignment_full,
            "Лемма": lemmas_full,
            "Тэги": tags_full,
            "Часть речи": pos_full,
        },
        index=[sent_list_for_index, tokenized_text],
    )
    # print(text_data.head(20))

    manual_alignment = []
    for i in range(
        len(alignments_list_full[0:20])
    ):  # пока ограничиваемся несколькими первыми словоформами для тестирования
        if len(alignments_list_full[i]) == 1:
            manual_alignment.append(alignments_list_full[i][0])
        if len(alignments_list_full[i]) > 1:
            print(f"\n[INFO]Словоформа: {tokenized_text[i]}\n")
            print(f"[INFO] Предложение: {sent_list_for_index[i]}")
        for j in range(len(alignments_list_full[i])):
            print(j, alignments_list_full[i][j])
            manual_alignment.append(alignments_list_full[i][int(0)])

    print(len(manual_alignment))

    tags_manual = []
    lemmas_manual = []
    pos_manual = []
    for alignment in manual_alignment:
        tags_manual.append(str(alignment.tag))
        lemmas_manual.append(alignment.normal_form)
        pos_manual.append(alignment.tag.POS)

    alignment_table = pd.DataFrame(
        data={
            "Предложение": sent_list_for_index[
                0:20
            ],  # в квадратных скобках указываем интервал
            "Словоформа": tokenized_text[0:20],
            "Варианты разметки": alignments_list_full[0:20],
            "Вероятная разметка": probable_alignment_full[0:20],
            "Ручная разметка": manual_alignment,
            "Лемма": lemmas_manual,
            "Часть речи": pos_manual,
            "Тэги": tags_manual,
        },
        index=[sent_list_for_index[0:20], tokenized_text[0:20]],
    )
    alignment_table.to_csv("table" + video_name)


start_app_time = timer()  # отсчёт с начала работы программы

# download_audio()
transcribe_audio()

# make_alignment(
#     "downloaded_audio\Python Programming 35 - How to Convert String to List using split\Python Programming 35 - How to Convert String to List using split.txt"
# )


overall_app_time = timer() - start_app_time  # общий подсчёт времени

print(
    f"\n[INFO] Работа завершена.\nОбщее время работы программы: {round(overall_app_time)} секунд(а).\n"
)
