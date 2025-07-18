"""
Discord Log Bot - Система логирования событий Discord сервера

Модульная архитектура:
- config: Управление настройками и конфигурацией
- events: Обработчики событий Discord
- ui: Пользовательский интерфейс (кнопки, модалы)
- commands: Команды бота
- utils: Вспомогательные функции
"""

__version__ = "2.0.0"
__author__ = "KaradevFaceKid"

from .analytics import analytics_manager 