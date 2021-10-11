import datetime

from django.utils import timezone

from cor.exception.app_exception import AppException
from intg.cfg.cfgModels import IntgCircuit


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

    # Логи объектов по сессии: ИД сессии: ИД объекта: Список логов
    _object_log_by_session_dict = {}

    # Логи сессии: ИД сессии: Список логов
    _session_log_by_session_dict = {}

    # Список ошибочных объектов сессии: ИД сессии: Список ИД объектов
    _error_object_by_session_dict = {}

    # Контур, для которого запущена интеграци
    circuit = None

    # Пользователь, под которым выполняются изменения
    s_user = 'Integration'


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
        log_dict = self._object_log_by_session_dict[session_id]

        if object_id not in log_dict:
            log_dict[object_id] = []

        log_dict[object_id].append(text)

    def write_session_log(self, text, n_direction):
        # Запись информационного лога сессии
        session_id = self._get_session_by_direction(n_direction)
        log_list = self._session_log_by_session_dict[session_id]
        log_list.append(text)

    def _new_session(self, n_direction):
        """Создание новой сессии обменов.
        """
        session_id = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S__") + str(n_direction)

        if n_direction == self.export_direction:
            self._export_session_id = session_id
        else:
            self._import_session_id = session_id

        # инициализируем логовые структуры
        self._object_log_by_session_dict[session_id] = {}
        self._error_object_by_session_dict[session_id] = []
        self._session_log_by_session_dict[session_id] = []

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
            object_log_dict = self._object_log_by_session_dict[session_id]

            if object_id not in object_log_dict:
                self.write_info_log(object_id, "OK", n_direction)
        except AppException as err:
            object_id = obj_info.id_external

            if not object_id:
                object_id = "Неизвестный объект"

            self.write_error_log(object_id, str(err), n_direction)

    def run(self, circuit):
        """Запуск интеграции"""

        self.circuit = circuit

        self.on_start_run()

        if self.is_export_enabled:
            self.run_export()

        if self.is_import_enabled:
            self.run_import()

        self.on_finish_run()

    def run_export(self):
        """Запуск экспорта"""
        session_id = self._new_session(self.export_direction)
        self.write_session_log("Экспорт по контуру " + str(self.circuit) + " начался", self.export_direction)
        self.on_export()
        self.write_session_log("Экспорт по контуру " + str(self.circuit) + " завершился", self.export_direction)

    def run_import(self):
        """Запуск импорта"""
        session_id = self._new_session(self.import_direction)
        self.write_session_log("Импорт по контуру " + str(self.circuit) + " начался", self.import_direction)
        self.on_import()
        self.write_session_log("Импорт по контуру " + str(self.circuit) + " завершился", self.import_direction)

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

    def on_start_run(self):
        """Действия выполняемые перед запуском обменов"""

    def on_finish_run(self):
        """Действия выполняемые после запуска обменов"""

    def has_errors(self):
        # Признак, что во время обменов произошли ошибки
        for session_id in [self._export_session_id, self._import_session_id]:
            if session_id:
                if self._error_object_by_session_dict[session_id]:
                    return True

        return False

    def get_report(self):
        # Получить отчет о выполнении

        lines = []

        for session_id in [self._export_session_id, self._import_session_id]:
            if session_id:
                lines.append("-------------------------")
                lines.append("Логи сессии")
                lines.append("-------------------------")
                for session_log in self._session_log_by_session_dict[session_id]:
                    lines.append(session_log)

                lines.append("-------------------------")
                lines.append("Логи объектов")
                lines.append("-------------------------")
                for object_id in self._object_log_by_session_dict[session_id]:
                    text = object_id
                    text = text + ': '
                    if object_id in self._error_object_by_session_dict[session_id]:
                        text = text + 'ОШИБКА'
                    else:
                        text = text + 'успешно'
                    lines.append(text)
                    for object_log in self._object_log_by_session_dict[session_id][object_id]:
                        lines.append('  ' + object_log)

        return lines


class ObjectInfo:
    """Информация об интегрируемом объекте"""
    # Идентификатор объекта во внешней системе
    id_external = None

