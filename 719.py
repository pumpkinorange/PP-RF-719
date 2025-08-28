# ссылка: https://gisp.gov.ru/pp719v2/mptapp/view/dl/production_res_valid_only/
# ОКПД2: 28.41, 26.20.40.150, 25.73.40.276, 28.49.21, 28.49.23
import os
import requests
import pandas as pd
from io import BytesIO
import time
import logging
from tqdm import tqdm
import json

def get_script_dir():
    """Возвращает абсолютный путь к директории скрипта"""
    return os.path.dirname(os.path.abspath(__file__))

def load_replacements():
    """Автоматически загружает конфиг из папки со скриптом"""
    config_path = os.path.join(get_script_dir(), "replacements.json")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("REPLACEMENTS", {})
    except FileNotFoundError:
        logging.error(f"Конфиг-файл не найден в папке скрипта: {config_path}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Ошибка формата в файле: {config_path}")
        return {}
    except Exception as e:
        logging.error(f"Ошибка загрузки конфига: {str(e)}")
        return {}

def main():
    total_start = time.time()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Загрузка замен
    replacements = load_replacements()
    if not replacements:
        logging.error("Работа прекращена из-за ошибки загрузки конфига")
        return

    # Этап 1: Ввод данных
    input_start = time.time()
    url = input("Введите URL файла (Ссылка кнопки 'Скачать только действующие (XLSX)'): ").strip()
    if not url:
        logging.error("Ошибка: URL не может быть пустым.")
        return
    codes_input = input("Введите код(ы) ОКПД-2 для фильтрации базы ПП РФ №719 через запятую: ").strip()
    if not codes_input:
        logging.error("Ошибка: не указан(ы) код(ы) для фильтрации.")
        return
    codes = [code.strip() for code in codes_input.split(",")]
    input_time = time.time() - input_start
    logging.info(f"[1] Ввод данных: {input_time:.3f} сек.")
    
    # Общий прогресс-бар для этапов 2-6
    with tqdm(total=5, desc="Общий прогресс") as main_pbar:
        # Этап 2: Скачивание файла
        download_start = time.time()
        response = None
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 1024
            progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc="Скачивание файла")
            buffer = BytesIO()
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    buffer.write(chunk)
                    progress_bar.update(len(chunk))
            progress_bar.close()
            content = buffer.getvalue()
        except Exception as e:
            logging.error(f"Ошибка при загрузке: {str(e)}")
            if 'progress_bar' in locals():
                progress_bar.close()
            return
        finally:
            if response:
                response.close()
        download_time = time.time() - download_start
        logging.info(f"[2] Скачивание файла: {download_time:.3f} сек.")
        main_pbar.update(1)
        
        # Этап 3: Чтение данных
        read_start = time.time()
        columns_to_load = [0, 1, 8, 9, 11, 12, 13, 15, 19, 23, 24]
        try:
            df = pd.read_excel(
                BytesIO(content),
                engine="openpyxl",
                usecols=columns_to_load, # выбор нужных колонок
                header=2, # заголовок с третьей строки
                dtype=str
            )
            df.rename(columns={df.columns[0]: "Organization"}, inplace=True)
        except Exception as e:
            logging.error(f"Ошибка чтения файла: {str(e)}")
            return
        read_time = time.time() - read_start
        logging.info(f"[3] Чтение данных: {read_time:.3f} сек.")
        main_pbar.update(1)
        
        # Этап 4: Фильтрация данных
        filter_start = time.time()
        try:
            pattern = "|".join(codes)
            filtered_df = df[df.iloc[:, 5].str.contains(pattern, na=False)].copy()
        except Exception as e:
            logging.error(f"Ошибка фильтрации: {str(e)}")
            return
        filter_time = time.time() - filter_start
        logging.info(f"[4] Фильтрация данных: {filter_time:.3f} сек.")
        main_pbar.update(1)
        
        # Этап 4.5: Замена названий (используем конфиг)
        replace_start = time.time()
        try:
            for pattern, replacement in replacements.items():
                filtered_df["Organization"] = filtered_df["Organization"].str.replace(
                    pattern, 
                    replacement,
                    regex=True,
                    case=False
                )
        except Exception as e:
            logging.error(f"Ошибка замены названий: {str(e)}")
            return
        replace_time = time.time() - replace_start
        logging.info(f"[4.5] Замена названий: {replace_time:.3f} сек.")
        main_pbar.update(1)
        
        # Этап 5: Сохранение результата
        save_start = time.time()
        try:
            filtered_df.to_excel("filtered_production_res.xlsx", index=False, engine="openpyxl")
        except Exception as e:
            logging.error(f"Ошибка сохранения: {str(e)}")
            return
        save_time = time.time() - save_start
        logging.info(f"[5] Сохранение результата: {save_time:.3f} сек.")
        main_pbar.update(1)
    
    total_time = time.time() - total_start
    logging.info(f"\n✅ Готово! Общее время: {total_time:.3f} сек.")

if __name__ == "__main__":
    main()