"""
Скрипт для извлечения фундаментальных данных из PDF отчетов Газпрома
Invest MRSU - Fundamentals Extractor

Использование:
    python extract_fundamentals.py

Требования:
    pip install PyPDF2 pdfplumber pandas openpyxl
"""

import sys
import os
import re
from pathlib import Path
import pandas as pd

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Извлечь текст из PDF файла

    Использует два метода:
    1. pdfplumber (более точный)
    2. PyPDF2 (fallback)
    """
    text = ""

    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        print(f"[OK] Извлечено {len(text)} символов из {os.path.basename(pdf_path)}")
        return text

    except ImportError:
        print("[!] pdfplumber не установлен. Используем PyPDF2...")

        try:
            import PyPDF2

            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"

            print(f"[OK] Извлечено {len(text)} символов из {os.path.basename(pdf_path)}")
            return text

        except ImportError:
            print("[ERROR] Установите pdfplumber или PyPDF2:")
            print("  pip install pdfplumber PyPDF2")
            return ""
        except Exception as e:
            print(f"[ERROR] Ошибка при чтении PDF: {e}")
            return ""


def extract_financial_metrics(text: str, year: int) -> dict:
    """
    Извлечь ключевые финансовые метрики из текста отчета

    Ищет:
    - Выручка (Revenue)
    - EBITDA
    - Чистая прибыль (Net Income)
    - Долг (Debt)
    - Дивиденды (Dividends)
    """

    metrics = {
        'year': year,
        'quarter': 'FY',  # Full Year
        'revenue_bn': None,
        'ebitda_bn': None,
        'net_profit_bn': None,
        'debt_bn': None,
        'dividend_per_share': None,
    }

    # Паттерны для поиска (регулярные выражения)
    patterns = {
        'revenue': [
            r'Выручка[^\d]+([\d\s,\.]+)\s*млрд',
            r'Revenue[^\d]+([\d\s,\.]+)\s*billion',
            r'Продажи[^\d]+([\d\s,\.]+)\s*млрд',
        ],
        'ebitda': [
            r'EBITDA[^\d]+([\d\s,\.]+)\s*млрд',
            r'ЕБИТДА[^\d]+([\d\s,\.]+)\s*млрд',
        ],
        'net_profit': [
            r'Чистая прибыль[^\d]+([\d\s,\.]+)\s*млрд',
            r'Net (?:income|profit)[^\d]+([\d\s,\.]+)\s*billion',
        ],
        'debt': [
            r'Долг[^\d]+([\d\s,\.]+)\s*млрд',
            r'Debt[^\d]+([\d\s,\.]+)\s*billion',
            r'Заемные средства[^\d]+([\d\s,\.]+)\s*млрд',
        ],
        'dividend': [
            r'Дивиденд[^\d]+([\d\s,\.]+)\s*(?:руб|₽)',
            r'Dividend[^\d]+([\d\s,\.]+)',
        ],
    }

    # Поиск метрик
    for metric_name, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(' ', '').replace(',', '.')
                try:
                    value = float(value_str)

                    if metric_name == 'revenue':
                        metrics['revenue_bn'] = value
                    elif metric_name == 'ebitda':
                        metrics['ebitda_bn'] = value
                    elif metric_name == 'net_profit':
                        metrics['net_profit_bn'] = value
                    elif metric_name == 'debt':
                        metrics['debt_bn'] = value
                    elif metric_name == 'dividend':
                        metrics['dividend_per_share'] = value

                    break  # Нашли значение, переходим к следующей метрике
                except ValueError:
                    continue

    return metrics


def process_financial_reports(reports_dir: str = ".") -> pd.DataFrame:
    """
    Обработать все финансовые отчеты

    Args:
        reports_dir: Директория с PDF отчетами

    Returns:
        DataFrame с извлеченными метриками
    """

    print("\n" + "="*80)
    print("[ОБРАБОТКА ФИНАНСОВЫХ ОТЧЕТОВ]")
    print("="*80 + "\n")

    # Поиск PDF файлов с финансовыми отчетами
    pdf_files = []
    for root, dirs, files in os.walk(reports_dir):
        for file in files:
            if 'financial-report' in file.lower() and file.endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))

    print(f"[INFO] Найдено отчетов: {len(pdf_files)}")

    all_metrics = []

    for pdf_path in sorted(pdf_files):
        filename = os.path.basename(pdf_path)

        # Извлечь год из названия файла
        year_match = re.search(r'20(\d{2})', filename)
        if not year_match:
            print(f"[!] Не удалось определить год для {filename}, пропускаем...")
            continue

        year = int("20" + year_match.group(1))

        print(f"\n[ОБРАБОТКА] {filename} (год: {year})")

        # Извлечь текст
        text = extract_text_from_pdf(pdf_path)

        if not text:
            print(f"[!] Не удалось извлечь текст из {filename}")
            continue

        # Извлечь метрики
        metrics = extract_financial_metrics(text, year)
        all_metrics.append(metrics)

        # Показать результаты
        print(f"  Выручка: {metrics['revenue_bn']} млрд руб.")
        print(f"  EBITDA: {metrics['ebitda_bn']} млрд руб.")
        print(f"  Чистая прибыль: {metrics['net_profit_bn']} млрд руб.")
        print(f"  Долг: {metrics['debt_bn']} млрд руб.")
        print(f"  Дивиденд: {metrics['dividend_per_share']} руб.")

    # Создать DataFrame
    df = pd.DataFrame(all_metrics)
    df = df.sort_values('year')

    print("\n" + "="*80)
    print("[РЕЗУЛЬТАТ]")
    print("="*80)
    print(df.to_string(index=False))

    return df


def merge_with_existing_data(fundamentals_df: pd.DataFrame, excel_path: str) -> pd.DataFrame:
    """
    Объединить извлеченные данные с существующими Excel данными от экономистов

    Args:
        fundamentals_df: DataFrame с данными из PDF
        excel_path: Путь к Excel файлу от экономистов

    Returns:
        Объединенный DataFrame
    """

    print("\n[ОБЪЕДИНЕНИЕ С ДАННЫМИ ЭКОНОМИСТОВ]")

    if not os.path.exists(excel_path):
        print(f"[!] Файл {excel_path} не найден, используем только данные из PDF")
        return fundamentals_df

    try:
        # Читаем данные экономистов
        excel_df = pd.read_excel(excel_path)

        print(f"[OK] Загружен файл: {os.path.basename(excel_path)}")
        print(f"  Строк: {len(excel_df)}")
        print(f"  Колонок: {len(excel_df.columns)}")

        # Здесь можно добавить логику объединения, если нужно
        # Пока просто возвращаем данные из PDF

        return fundamentals_df

    except Exception as e:
        print(f"[ERROR] Ошибка при чтении Excel: {e}")
        return fundamentals_df


def save_to_csv(df: pd.DataFrame, output_path: str = "dataset/fundamentals/GAZP_fundamentals.csv"):
    """
    Сохранить результаты в CSV для ML модели
    """

    print(f"\n[СОХРАНЕНИЕ] {output_path}")

    # Создать директорию если не существует
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Сохранить
    df.to_csv(output_path, index=False, encoding='utf-8')

    print(f"[OK] Файл сохранен: {output_path}")
    print(f"  Строк: {len(df)}")
    print(f"  Колонок: {len(df.columns)}")


def main():
    """Главная функция"""

    print("="*80)
    print("  ИЗВЛЕЧЕНИЕ ФУНДАМЕНТАЛЬНЫХ ДАННЫХ")
    print("  Invest MRSU - Fundamentals Extractor")
    print("="*80)

    # Корневая директория проекта
    project_root = r"c:\Users\Sergej\Documents\GitHub\investApp"

    # Обработать финансовые отчеты
    fundamentals_df = process_financial_reports(project_root)

    if fundamentals_df.empty:
        print("\n[!] Не удалось извлечь данные из PDF отчетов")
        print("[NOTE] Убедитесь, что установлены необходимые библиотеки:")
        print("  pip install pdfplumber PyPDF2")
        return

    # Объединить с данными экономистов (опционально)
    excel_path = os.path.join(project_root, "Сводка данных по Газпрому.xlsx")
    final_df = merge_with_existing_data(fundamentals_df, excel_path)

    # Сохранить результат
    output_path = os.path.join(project_root, "invest_mrsu", "dataset", "fundamentals", "GAZP_fundamentals.csv")
    save_to_csv(final_df, output_path)

    print("\n" + "="*80)
    print("[OK] ГОТОВО!")
    print("="*80)
    print("\n[СЛЕДУЮЩИЕ ШАГИ]")
    print("1. Проверьте извлеченные данные в CSV файле")
    print("2. При необходимости дополните вручную недостающие метрики")
    print("3. Используйте этот файл для обучения ML модели")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
