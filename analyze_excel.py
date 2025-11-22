"""
Скрипт для анализа Excel файлов, подготовленных экономистами
Показывает структуру данных для адаптации ML модели
"""

import pandas as pd
import os
import sys
from pathlib import Path

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def analyze_excel_file(file_path: str):
    """Анализирует структуру Excel файла"""
    print("\n" + "="*80)
    print(f"[АНАЛИЗ ФАЙЛА] {os.path.basename(file_path)}")
    print("="*80 + "\n")

    try:
        # Читаем все листы
        excel_file = pd.ExcelFile(file_path)
        print(f"[ЛИСТЫ] Найдено: {len(excel_file.sheet_names)}")
        print(f"   Названия: {', '.join(excel_file.sheet_names)}\n")

        # Анализируем каждый лист
        for sheet_name in excel_file.sheet_names:
            print(f"\n{'-'*80}")
            print(f"[ЛИСТ] '{sheet_name}'")
            print(f"{'-'*80}")

            df = pd.read_excel(file_path, sheet_name=sheet_name)

            print(f"\n[РАЗМЕР] {df.shape[0]} строк x {df.shape[1]} колонок")

            print(f"\n[КОЛОНКИ]")
            for i, col in enumerate(df.columns, 1):
                col_type = df[col].dtype
                non_null = df[col].notna().sum()
                null_count = df[col].isna().sum()
                print(f"   {i}. '{col}' [{col_type}] - {non_null} заполнено, {null_count} пропусков")

            print(f"\n[ПЕРВЫЕ 5 СТРОК]")
            print(df.head().to_string(index=True))

            print(f"\n[ПОСЛЕДНИЕ 3 СТРОКИ]")
            print(df.tail(3).to_string(index=True))

            # Статистика для числовых колонок
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                print(f"\n[СТАТИСТИКА ЧИСЛОВЫХ КОЛОНОК]")
                print(df[numeric_cols].describe().to_string())

            # Проверка дат
            date_cols = df.select_dtypes(include=['datetime64']).columns
            if len(date_cols) > 0:
                print(f"\n[ИНФОРМАЦИЯ О ДАТАХ]")
                for col in date_cols:
                    print(f"   {col}: {df[col].min()} -> {df[col].max()}")
            else:
                # Попытка найти колонки с датами (если они как текст)
                potential_date_cols = [col for col in df.columns if 'дат' in col.lower() or 'date' in col.lower()]
                if potential_date_cols:
                    print(f"\n[!] Потенциальные колонки с датами (не в формате datetime):")
                    for col in potential_date_cols:
                        print(f"   {col}: {df[col].iloc[0]} -> {df[col].iloc[-1]}")

            print(f"\n[КАЧЕСТВО ДАННЫХ]")
            total_cells = df.shape[0] * df.shape[1]
            filled_cells = df.notna().sum().sum()
            print(f"   Заполненность: {filled_cells}/{total_cells} ({filled_cells/total_cells*100:.1f}%)")

            # Предупреждения
            if df.duplicated().any():
                print(f"   [!] Найдено {df.duplicated().sum()} дублирующихся строк")

    except Exception as e:
        print(f"[ERROR] Ошибка при чтении файла: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Главная функция"""
    print("="*80)
    print("  АНАЛИЗ ДАННЫХ ЭКОНОМИСТОВ")
    print("  Invest MRSU - Data Analysis Tool")
    print("="*80)

    # Файлы для анализа
    files = [
        r"c:\Users\Sergej\Documents\GitHub\investApp\Сводка данных по Газпрому.xlsx",
        r"c:\Users\Sergej\Documents\GitHub\investApp\Сводка_данных_по_Сургутнефтегаз_2020_2024_год.xlsx"
    ]

    for file_path in files:
        if os.path.exists(file_path):
            analyze_excel_file(file_path)
        else:
            print(f"\n[ERROR] Файл не найден: {file_path}")

    print("\n" + "="*80)
    print("[OK] АНАЛИЗ ЗАВЕРШЕН")
    print("="*80)

    print("\n[NOTE] Рекомендации будут основаны на этой структуре данных")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
