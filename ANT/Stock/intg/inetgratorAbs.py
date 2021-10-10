import datetime

from cor.exception.app_exception import AppException


class IntegratorAbs:
    """Абстрактный класс для реализции интеграции"""

    # Признак, что экспорт включен
    is_export_enabled = True

    # Признак, что импорт включен
    is_import_enabled = True

    # Направление Экспорта
    export_direction = 1

    # Направление Импорта
    import_direction = -1

    # ИД сессии экспорта
    _export_session_id = None

    # ИД сессии импорта
    _import_session_id = None

    # Логи по сессии: ИД сессии: ИД объекта: Список логов
    _log_by_session_dict = {}

    # Список ошибочных объектов сессии: ИД сессии: Список ИД объектов
    _error_object_by_session_dict = {}

    def _get_session_by_direction(self, n_direction):
        # Получение ИД сессии по направлению интеграции
        if n_direction == self.export_direction:
            return self._export_session_id
        else:
            return self._import_session_id

    def write_error_log(self, object_id, text, n_direction):
        # Запись ошибочного лога

        session_id = self._get_session_by_direction(n_direction)
        # Пишем лог
        self.write_info_log(object_id, text, n_direction)
        # Отмечаем объект как ошибочный
        self._error_object_by_session_dict[session_id].append(object_id)

    def write_info_log(self, object_id, text, n_direction):
        # Запись информационного лога
        session_id = self._get_session_by_direction(n_direction)
        log_dict = self._log_by_session_dict[session_id]

        if object_id not in log_dict:
            log_dict[object_id] = []

        log_dict[object_id].append(text)

    def _new_session(self, n_direction):
        """Создание новой сессии обменов.
        """
        session_id = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S__") + str(n_direction)

        if n_direction == self.export_direction:
            self._export_session_id = session_id
        else:
            self._import_session_id = session_id

        # инициализируем логовые структуры
        self._log_by_session_dict[session_id] = {}
        self._error_object_by_session_dict[session_id] = []

        return session_id

    def handle_object(self, n_direction, handler):
        """Выполнение обработчика по объекту
        На вход направление интеграции и обработчик объекта, который должен принимать ObjectInfo.
        После того, как станет известно, что за объект интегрируется, обработчик должен заполнить о нем информацию о ObjectInfo"""
        obj_info = ObjectInfo()
        session_id = self._get_session_by_direction(n_direction)

        try:
            handler(obj_info)

            object_id = obj_info.id_external

            if not object_id:
                raise AppException("Не указан ИД объекта")

            # проверим, если в лог не написали нечего, то добавим инфу, что объект загрузился
            object_log_dict = self._log_by_session_dict[session_id]

            if object_id not in object_log_dict:
                self.write_info_log(object_id, "OK", n_direction)
        except Exception as err:
            object_id = obj_info.id_external

            if not object_id:
                object_id = "Неизвестный объект"

            self.write_error_log(object_id, str(err), n_direction)

    def run(self):
        """Запуск интеграции"""
        if self.is_export_enabled:
            self.run_export()

        if self.is_import_enabled:
            self.run_import()

    def run_export(self):
        """Запуск экспорта"""
        session_id = self._new_session(self.export_direction)
        self.on_import()

    def run_import(self):
        """Запуск импорта"""
        session_id = self._new_session(self.import_direction)
        self.on_import()

    def on_import(self):
        """Действия выполняемые при импорте.
        Требуется переопределить этот метод в наследнике.
        Метод должен получать список объекто исмпорта, и для каждого вызывать handle_object
        Если экспорт не используется, то отключите флаг is_export_enabled"""
        raise AppException("Не реализован импорт объектов")

    def on_export(self):
        """Действия выполняемые при экспорте.
        Требуется переопределить этот метод в наследнике.
        Метод должен получать список объекто экспорта, и для каждого вызывать handle_object
        Если импорт не используется, то отключите флаг is_import_enabled"""
        raise AppException("Не реализован экспорт объектов")


class ObjectInfo:
    """Информация об интегрируемом объекте"""
    # Идентификатор объекта во внешней системе
    id_external = None
