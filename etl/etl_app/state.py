import json
import logging
import pathlib
from typing import Any

logger = logging.getLogger()


class JsonFileStorage:
    def check_json_file(self):
        if not pathlib.Path(self.file_path).is_file():
            raise FileNotFoundError('Wrong path to json file storage.')
        if pathlib.PurePosixPath(self.file_path).suffix != '.json':
            raise TypeError('File\'s extension isn\'t .json')

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.check_json_file()

    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        try:
            with open(self.file_path, 'r', encoding='utf8') as file:
                d = json.loads(file.read())
                return d
        except json.JSONDecodeError:
            return {}

    def save_state(self, state: dict = None) -> None:
        """Сохранить состояние в постоянное хранилище"""
        j_dict = self.retrieve_state()
        with open(self.file_path, 'w', encoding='utf8') as file:
            state = {**j_dict, **state}
            file.write(json.dumps(state))


class State:
    """
    Класс для хранения состояния при работе с данным, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределенным хранилищем.
    """

    def __init__(self, storage: JsonFileStorage):
        self.storage = storage
        self.state_dict = self.storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определенного ключа"""
        self.storage.save_state({key: value})

    def get_state(self, key: str = None) -> Any:
        """Получить состояние по отпределенному ключу"""
        if not key:
            return None
        try:
            return self.state_dict[key]
        except KeyError as err:
            logger.error(err)
