import pandas as pd

def load_file_with_encoding(file_path):
    if file_path.endswith('.csv'):
        encodings = ['utf-8', 'cp1251', 'latin-1', 'windows-1251', 'iso-8859-1']
        for enc in encodings:
            try:
                return pd.read_csv(file_path, encoding=enc)
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError("Не удалось прочитать CSV. Попробуйте сохранить в UTF-8.")
    else:
        return pd.read_excel(file_path)
