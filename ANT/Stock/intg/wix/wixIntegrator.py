import requests
from django.utils import dateparse

from cor.exception.app_exception import AppException
from intg.cfg.mapping.mappingModels import GoodMapping, DeliverySystemMapping
from intg.inetgratorAbs import IntegratorAbs, ObjectInfo
from ebaysdk.trading import Connection as Trading
import json

from intg.cfg.cfgModels import IntgCircuit, IntgCircuitRunTimeData
from trd.order.orderModels import TrdOrderState, TrdOrder, TrdOrderDet
from datetime import datetime, timedelta


class WixIntegrator(IntegratorAbs):
    """Реализация интеграции с Wix"""

    # Параметры, требуемые для подключения
    url = None
    secret = None

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
        self.url = json_data.get('url')
        self.secret = json_data.get('secret')

        # Загружаем меппинги
        self.mapping_goods_dict = GoodMapping.get_by_circuit(self.circuit)
        self.mapping_delivery_service_dict = DeliverySystemMapping.get_by_circuit(self.circuit)

    def import_order(self, order, obj_info):
        """Импорт одного заказа"""

        # ИД заказа
        order_id = str(order.get('number'))
        obj_info.id_external = order_id

        # Требуется сразу же сохранить новый заказ, т.к. сесии выгрузки запоминают дату последней выгрузки
        # и получают заказы начиная с даты последней выгрузки. Если сохранять все заказы, то они будут обработаны
        # новыми сессиями как незавршенные

        trd_order = TrdOrder.objects.filter(s_reg_num=order_id, id_trade_system=self.circuit.id_trade_system).first()

        if not trd_order:
            trd_order = TrdOrder.inset_by_trade_system(self.circuit.id_trade_system, self.s_user)
            trd_order.set_s_reg_num(order_id)
            trd_order.save()

        # Оплачен
        is_payed = order.get('paymentStatus') == "PAID"
        # Завершен
        is_finished = order.get('fulfillmentStatus') == "FULFILLED"
        # Дата создания
        created_time = order.get('_dateCreated')
        # Получатель
        shipping_address_name = None
        # Адрес
        shipping_address_address = None
        # Набор трек номеров
        shipment_tracking_number = None
        # ПРоданные позиции
        selled_sku_list = []
        # Способ доставки
        delivery_option = None

        # Расчет адреса
        shipping_info = order.get('shippingInfo')
        if shipping_info:
            delivery_option = shipping_info.get('deliveryOption')
            shipment_details = shipping_info.get('shipmentDetails')
            if shipment_details:
                # Получатель
                shipping_address_name = str(shipment_details.get('lastName')) + ' ' + str(
                    shipment_details.get('firstName'))
                address = shipment_details.get('address')
                if address:
                    # Адрес
                    shipping_address_address = address.get('formatted')

        # Трек номер
        fulfillments = order.get('fulfillments')
        if fulfillments:
            for fulfillment in fulfillments:
                tracking_info = fulfillment.get('trackingInfo')
                if tracking_info:
                    shipment_tracking_number = tracking_info.get('trackingNumber')

        # Товары
        line_items = order.get('lineItems')
        if line_items:
            for line_item in line_items:
                gds_id = line_item.get('name')
                n_qty = line_item.get('quantity')

                gds_dict = {
                    "id": gds_id,
                    "qty": n_qty
                }

                options = line_item.get('options')
                if options:
                    gds_dict["options"] = []
                    for option in options:
                        if option.get('selection') == "да":
                            gds_dict["options"].append(option.get("option"))

                selled_sku_list.append(gds_dict)


        # установка данных
        # сначала откатим заказ, т.к. он мог уже внести данные в склад
        old_state = trd_order.id_state
        if trd_order.id_state.is_write_off_goods():
            trd_order.set_id_state(TrdOrderState.get_start_state().id, self.s_user)

        trd_order.set_d_reg_date(self.__str_to_date(created_time))
        trd_order.set_s_receiver(shipping_address_name)
        trd_order.set_s_address(shipping_address_address)
        trd_order.set_s_track_num(shipment_tracking_number)

        trd_order.save()

        # Служба доставки
        if delivery_option:
            delivery_service = self.mapping_delivery_service_dict.get(delivery_option)
            if not delivery_service:
                raise AppException('Для службы доставки '+ delivery_option + ' не настроено сопоставление')
            trd_order.set_id_delivery_service(delivery_service)
        else:
            trd_order.set_id_delivery_service(None)

        trd_order.save()

        # Обработка ТМЦ
        selled_goods_dict = {}

        for selled_sku in selled_sku_list:
            external_id = selled_sku["id"]
            external_qty = selled_sku["qty"]

            mapping_goods = self.mapping_goods_dict.get(external_id)

            if not mapping_goods:
                raise AppException('Для товара '+ external_id + ' не настроено сопоставление')

            # Сам товар
            for good, n_qty in mapping_goods[GoodMapping.good_mapping_key()]:

                if good not in selled_goods_dict:
                    selled_goods_dict[good] = 0

                selled_goods_dict[good] = selled_goods_dict[good] + n_qty * external_qty

            # Опции товара
            options = selled_sku.get('options')
            if options:
                for option in options:
                    mapping_option = mapping_goods[GoodMapping.option_mapping_key()].get(option)

                    if not mapping_option:
                        raise AppException('Для товара ' + external_id + ' не настроено сопоставление опции ' + option)

                    for good, n_qty in mapping_option:

                        if good not in selled_goods_dict:
                            selled_goods_dict[good] = 0

                        selled_goods_dict[good] = selled_goods_dict[good] + n_qty * external_qty

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
        if is_finished:
            # Из Wix нельзя понять, что заказ доставлен. ПОтому если ему вручную
            # было установлено состояние большее, чем отправлен, то ставим его
            state = TrdOrderState.objects.filter(n_order=400).first()
            if old_state.n_order > state.n_order:
                state = old_state

        if state:
            trd_order.set_id_state(state.id, self.s_user)

    def on_import(self):
        # Первый запрос, обрабатываем незаврешенные заказы
        unfinished_order_id_list = []
        for order in TrdOrder.objects.filter(
                id_trade_system=self.circuit.id_trade_system,
                id_state__n_order__lt=400
        ):
            unfinished_order_id_list.append(order.s_reg_num)

        if unfinished_order_id_list:
            params = {'order_id_array': ";".join(unfinished_order_id_list)}
            headers = {'secret': self.secret}
            response = requests.get(
                self.url,
                params=params,
                headers=headers
            )
            response.raise_for_status()

            response_json = response.json()

            response_order_list = response_json['orders']
            response_order_id_set = set()
            # Обрабатываем заказы
            for response_order in response_order_list:
                self.handle_object(
                    self.import_direction,
                    lambda obj_info: self.import_order(response_order, obj_info)
                )
                response_order_id_set.add(str(response_order.get('number')))

            # Проверим, что все заказы были в запросе
            for unfinished_order_id in unfinished_order_id_list:
                if unfinished_order_id not in response_order_id_set:
                    self.write_error_log(
                        unfinished_order_id,
                        "Для заказа " + unfinished_order_id + " не пришла информация от Wix",
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
            date = datetime.today() - timedelta(days=30)

            params = {'order_create_date': self.__date_to_str(date)}
            headers = {'secret': self.secret}
            response = requests.get(
                self.url,
                params=params,
                headers=headers
            )
            response.raise_for_status()

            response_json = response.json()

            response_order_list = response_json['orders']

            order_array = filter(
                lambda _order: _order.get('fulfillmentStatus') != "FULFILLED",
                response_order_list
            )

            response_time_str = response_json["date"]
            new_last_import_date = self.__str_to_date(response_time_str)
        else:
            params = {'order_create_date': last_import_date}
            headers = {'secret': self.secret}
            response = requests.get(
                self.url,
                params=params,
                headers=headers
            )
            response.raise_for_status()

            response_json = response.json()
            order_array = response_json.get('orders')
            response_time_str = response_json["date"]
            new_last_import_date = self.__str_to_date(response_time_str)

        if order_array:
            for order in order_array:
                self.handle_object(self.import_direction, lambda obj_info: self.import_order(order, obj_info) )

        # Сохраняем дату последней выгрузки
        json_runtime_data[key_last_import_date] = self.__date_to_str(new_last_import_date)

        circuit_runtime_data.s_json_data = json.dumps(json_runtime_data)
        circuit_runtime_data.save()
