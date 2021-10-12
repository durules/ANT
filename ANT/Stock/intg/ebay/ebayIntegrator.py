from django.utils import dateparse

from cor.exception.app_exception import AppException
from intg.cfg.mapping.mappingModels import GoodMapping, DeliverySystemMapping
from intg.inetgratorAbs import IntegratorAbs, ObjectInfo
from ebaysdk.trading import Connection as Trading
import json

from intg.cfg.cfgModels import IntgCircuit, IntgCircuitRunTimeData
from trd.order.orderModels import TrdOrderState, TrdOrder, TrdOrderDet
from datetime import datetime, timedelta


class EbayIntegrator(IntegratorAbs):
    """Реализация интеграции с Ebay"""

    # Параметры, требуемые для подключения
    app_id = None
    dev_id = None
    cert_id = None
    token = None

    # Меппинг ТМЦ
    mapping_goods_dict = {}

    # Меппинг служб доставки
    mapping_delivery_service_dict = {}

    is_import_enabled = True
    is_export_enabled = False

    def __str_to_date(self, str_value):
        return dateparse.parse_datetime(str_value)

    def __date_to_str(self, date_value):
        return date_value.isoformat().replace('+00:00', 'Z')

    def on_start_run(self):
        # Получаем параметры подключения

        if not self.circuit.s_config:
            raise AppException('Не указана конфигурация подключения контура ' + str(self.circuit))

        json_data = json.loads(self.circuit.s_config)
        self.app_id = json_data.get('appid')
        self.dev_id = json_data.get('devid')
        self.cert_id = json_data.get('certid')
        self.token = json_data.get('token')

        # Загружаем меппинги
        self.mapping_goods_dict = GoodMapping.get_by_circuit(self.circuit)
        self.mapping_delivery_service_dict = DeliverySystemMapping.get_by_circuit(self.circuit)

    def import_order(self, order, obj_info):
        """Импорт одного заказа"""

        # ИД заказа
        order_id = order.get('OrderID')
        obj_info.id_external = order_id

        # Требуется сразу же сохранить новый заказ, т.к. сесии выгрузки запоминают дату последней выгрузки
        # и получают заказы начиная с даты последней выгрузки. Если сохранять все заказы, то они будут обработаны
        # новыми сессиями как незавршенные

        trd_order = TrdOrder.objects.filter(s_reg_num=order_id, id_trade_system=self.circuit.id_trade_system).first()

        if not trd_order:
            trd_order = TrdOrder.inset_by_trade_system(self.circuit.id_trade_system, self.s_user)
            trd_order.set_s_reg_num(order_id)
            trd_order.save()


        # Дата оплаты
        paid_time = order.get('PaidTime')
        # Дата отправки
        shipped_time = order.get('ShippedTime')
        # Дата доставки
        actual_delivery_time = None
        # Дата создания
        created_time = order.get('CreatedTime')
        # Служба доставки
        shipping_service_name = None
        # Получатель
        shipping_address_name = None
        # Адрес
        shipping_address_address = None
        # Набор трек номеров
        shipment_tracking_number_set = set()
        # ПРоданные позиции
        selled_sku_dict = {}

        # Получение информации о доставке
        shipping_service_selected = order.get('ShippingServiceSelected')
        if shipping_service_selected:
            shipping_service_name = shipping_service_selected.get('ShippingService')
            shipping_package_info = shipping_service_selected.get('ShippingPackageInfo')
            if shipping_package_info:
                actual_delivery_time = shipping_package_info.get('ActualDeliveryTime')

        # Расчет адреса
        shipping_address = order.get('ShippingAddress')
        if shipping_address:
            shipping_address_name = shipping_address.get('Name')

            address_dict = {
                'Страна': 'CountryName',
                'Почтовый индекс': 'PostalCode',
                'Область': 'StateOrProvince',
                'Город': 'CityName',
                'Улица': 'Street1',
                'Улица2': 'Street2',
            }

            for key in address_dict:
                value = shipping_address.get(address_dict[key])
                if value:
                    if shipping_address_address:
                        shipping_address_address = shipping_address_address + '\n'
                    else:
                        shipping_address_address = ''
                    shipping_address_address = shipping_address_address + key + ': ' + value

        # Обработка позиций заказа
        transaction_array = order.get('TransactionArray')

        if not transaction_array:
            raise AppException("Не найден список позиций заказа")

        transaction = transaction_array.get('Transaction')

        if not transaction:
            raise AppException("Не найден список позиций заказа")

        for trans in transaction:
            # Расчет трек номера
            shipping_details = trans.get('ShippingDetails')
            if shipping_details:
                shipment_tracking_details = shipping_details.get('ShipmentTrackingDetails')
                if shipment_tracking_details:
                    shipment_tracking_number = shipment_tracking_details.get('ShipmentTrackingNumber')
                    if shipment_tracking_number:
                        shipment_tracking_number_set.add(shipment_tracking_number)

            # Расчет товаров
            item = trans.get('Item')
            if item:
                sku = item.get('SKU')
                title = item.get('Title')
                qty = int(trans.get('QuantityPurchased'))

                if not sku:
                    raise AppException('Для товара ' + title + ' не указан SKU')

                if sku in selled_sku_dict:
                    selled_sku_dict[sku] = selled_sku_dict[sku] + qty
                else:
                    selled_sku_dict[sku] = qty

        # установка данных
        # сначала откатим заказ, т.к. он мог уже внести данные в склад
        if trd_order.id_state.is_write_off_goods():
            trd_order.set_id_state(TrdOrderState.get_start_state().id, self.s_user)

        trd_order.set_d_reg_date(self.__str_to_date(created_time))
        trd_order.set_s_receiver(shipping_address_name)
        trd_order.set_s_address(shipping_address_address)
        trd_order.set_s_track_num(', '.join(shipment_tracking_number_set))

        trd_order.save()

        # Служба доставки
        if shipping_service_name:
            delivery_service = self.mapping_delivery_service_dict.get(shipping_service_name)
            if not delivery_service:
                raise AppException('Для службы доставки '+ shipping_service_name + ' не настроено сопоставление')
            trd_order.set_id_delivery_service(delivery_service)
        else:
            trd_order.set_id_delivery_service(None)

        trd_order.save()

        # Обработка ТМЦ
        selled_goods_dict = {}

        for selled_sku in selled_sku_dict:
            mapping_goods = self.mapping_goods_dict.get(selled_sku)

            if not mapping_goods:
                raise AppException('Для SKU '+ selled_sku + ' не настроено сопоставление')

            for good, n_qty in mapping_goods:

                if good not in selled_goods_dict:
                    selled_goods_dict[good] = 0

                selled_goods_dict[good] = selled_goods_dict[good] + n_qty * selled_sku_dict[selled_sku]

        order_det_by_good_dict = {}
        # индксируем позиции заказа
        for trd_order_det in TrdOrderDet.objects.filter(id_order=trd_order):
            order_det_by_good_dict[trd_order_det.id_good] = trd_order_det

        # удаляем позиции, которых нет
        for order_det_good in order_det_by_good_dict:
            if order_det_good not in selled_goods_dict:
                order_det_by_good_dict[order_det_good].delete()

        # применяем позиции
        for selled_goods in selled_goods_dict:
            trd_order_det = order_det_by_good_dict.get(selled_goods)

            if not trd_order_det:
                trd_order_det = TrdOrderDet.insert(trd_order.id, selled_goods.id)

            trd_order_det.set_n_qty(selled_goods_dict[selled_goods])
            trd_order_det.save()

        trd_order.save()

        # Обработка состояния
        state = None
        if actual_delivery_time:
            # Доставлен
            state = TrdOrderState.objects.filter(n_order=500).first()
        elif shipped_time:
            # Отправлен
            state = TrdOrderState.objects.filter(n_order=400).first()

        if state:
            trd_order.set_id_state(state.id, self.s_user)

    def on_import(self):
        api = Trading(domain='api.ebay.com',
                      appid=self.app_id, devid=self.dev_id,
                      certid=self.cert_id, token=self.token,
                      config_file=None, timeout=300
                      )

        # Первый запрос, обрабатываем незаврешенные заказы
        unfinished_order_id_list = []
        for order in TrdOrder.objects.filter(
                id_trade_system=self.circuit.id_trade_system,
                id_state__n_order__lt=TrdOrderState.get_is_finished_state_number()
        ):
            unfinished_order_id_list.append(order.s_reg_num)

        if unfinished_order_id_list:
            response = api.execute(
                'GetOrders',
                {
                    'OrderIDArray': {'OrderID': unfinished_order_id_list},
                    'OrderRole': 'Seller',
                }
            )

            response_order_list = self._get_order_list_from_response(response)
            response_order_id_set = set()
            # Обрабатываем заказы
            for response_order in response_order_list:
                self.handle_object(
                    self.import_direction,
                    lambda obj_info: self.import_order(response_order, obj_info)
                )
                response_order_id_set.add(response_order.get('OrderID'))

            # Проверим, что все заказы были в запросе
            for unfinished_order_id in unfinished_order_id_list:
                if unfinished_order_id not in response_order_id_set:
                    self.write_error_log(
                        unfinished_order_id,
                        "Для заказа " + unfinished_order_id + " не пришла информация от Ebay",
                        self.import_direction
                    )

        # Второй запрос, обрабатываем новые заказы
        # Получаем дату последнего запроса
        circuit_runtime_data = IntgCircuitRunTimeData.register_by_circuit(self.circuit)
        json_runtime_data = None

        key_last_import_date = 'lastImportDate'

        if circuit_runtime_data.s_json_data:
            json_runtime_data = json.loads(circuit_runtime_data.s_json_data)
        else:
            json_runtime_data = {}

        last_import_date = json_runtime_data.get(key_last_import_date)
        new_last_import_date = None
        order_array = []

        if not last_import_date:
            # Если это первая выгрузка? возмем все заказы за последние 30 дней, и загрузим только не завершенные?
            response = api.execute(
                'GetOrders',
                {
                    'OrderRole': 'Seller',
                    'NumberOfDays ': 30,
                    'OrderStatus': 'Completed'
                }
            )

            order_array = filter(
                lambda _order: self._is_response_order_not_shipped(_order),
                self._get_order_list_from_response(response)
            )

            response_time_str = response.dict()['Timestamp']
            new_last_import_date = self.__str_to_date(response_time_str)
        else:
            # Рассчет даты окончания. Ebay рекоменлдует делать текущее вермя минус 2 минуты

            response = api.execute('GetUser')
            response_time_str = response.dict()['Timestamp']
            response_time = self.__str_to_date(response_time_str)
            create_to_time = response_time - timedelta(minutes=2)

            response = api.execute(
                'GetOrders',
                {
                    'CreateTimeFrom': last_import_date,
                    'CreateTimeTo': self.__date_to_str(create_to_time),
                    'OrderRole': 'Seller',
                    'OrderStatus': 'Completed'
                }
            )
            order_array = self._get_order_list_from_response(response)

            new_last_import_date = create_to_time

        for order in order_array:
            self.handle_object(self.import_direction, lambda obj_info: self.import_order(order, obj_info) )

        # Сохраняем дату последней выгрузки
        json_runtime_data[key_last_import_date] = self.__date_to_str(new_last_import_date)

        circuit_runtime_data.s_json_data = json.dumps(json_runtime_data)
        circuit_runtime_data.save()

    def _get_order_list_from_response(self, response):
        order_dict = response.dict()['OrderArray']

        if order_dict:
            return order_dict['Order']
        else:
            return []

    def _is_response_order_not_shipped(self, order):
        """Проверка, что заказ, вернувшийся из не является оправленным"""
        order.get('ShippedTime')

    def run_by_single_order(self, order_id):
        """Запуск обменов по одному заказу"""
        self.on_start_run()

        api = Trading(domain='api.ebay.com',
                      appid=self.app_id, devid=self.dev_id,
                      certid=self.cert_id, token=self.token,
                      config_file=None, timeout=300
                      )

        response = api.execute(
            'GetOrders',
            {
                'OrderIDArray': {'OrderID': order_id},
                'OrderRole': 'Seller',
            }
        )

        response_order_list = self._get_order_list_from_response(response)
        for response_order in response_order_list:
            obj_info = ObjectInfo()
            self.import_order(response_order, obj_info)

