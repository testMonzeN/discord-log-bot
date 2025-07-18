class ConfigManager:
    """
    Класс для работы с настройками бота (bot_settings.json).
    """
    def __init__(self, path: str = 'bot_settings.json'):
        self.path = path
        self.data = self._load()

    def _load(self):
        import json, os
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"channel_log": {}, "bot_settings": {}}

    def save(self):
        import json
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_channel_log(self):
        return self.data.get("channel_log", {})

    def get_bot_settings(self):
        return self.data.get("bot_settings", {})

    def set_channel_log(self, value):
        self.data["channel_log"] = value
        self.save()

    def set_bot_settings(self, value):
        self.data["bot_settings"] = value
        self.save() 