"""
Модуль для автоматического резервного копирования файлов аналитики.
"""

import os
import shutil
from datetime import datetime

def backup_file(src_path: str, backup_dir: str = 'backups'):
    """
    Создаёт резервную копию файла src_path в папке backup_dir с уникальным именем по дате и времени.
    """
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    base = os.path.basename(src_path)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_name = f"{os.path.splitext(base)[0]}_{timestamp}.json"
    backup_path = os.path.join(backup_dir, backup_name)
    shutil.copy2(src_path, backup_path)
    return backup_path 