from cor.exception.app_exception import AppException
from intg.InetgratorAbs import IntegratorAbs
from ebaysdk.trading import Connection as Trading


class EbayIntegrator(IntegratorAbs):
    """Реализация интеграции с Ebay"""
    def __get_token(self):
        f = open("C:\Git\ANT\Stock\intg\ebay\ebay_token.txt", "r")
        res = f.read()
        return res

    is_import_enabled = True
    is_export_enabled = False

    def import_order(self, order, obj_info):
        """Импорт одного заказа"""

        # ИД заказа
        order_id = order.get('OrderID')
        obj_info.id_external = order_id

        # Дата оплаты
        paid_time = order.get('PaidTime')
        # Дата отправки
        shipped_time = order.get('ShippedTime')
        # Дата доставки
        actual_delivery_time = None
        # Дата создания
        created_time = order.get('CreatedTime')
        # Получатель
        shipping_address_name = None
        # Адрес
        shipping_address_address = None
        # Набор трек номеров
        shipment_tracking_number_set = set()
        # ПРоданные позиции
        selled_sku_dict = {}

        # рассчет даты доставки
        shipping_service_selected = order.get('ShippingServiceSelected')
        if shipping_service_selected:
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

        print(order_id)
        print(created_time)
        print(paid_time)
        print(shipped_time)
        print(actual_delivery_time)
        print(shipping_address_name)
        print(shipping_address_address)
        print(shipment_tracking_number_set)
        print(selled_sku_dict)

    def on_import(self):
        api = Trading(domain='api.ebay.com',
                      appid="AlekseyK-svarogmn-PRD-2a292be01-16024d26", devid="897bd038-a619-4206-b7eb-c2ca642b4b37",
                      certid="SBX-23495a34b3cd-991c-4300-9fc2-8def", token=self.__get_token(), config_file=None)

        response = api.execute(
            'GetOrders',
            {
                # 'CreateTimeFrom': '2021-10-01T00:05:08.100Z',
                # 'CreateTimeTo': '2021-10-30T18:05:08.100Z',
                'OrderIDArray': {'OrderID': ['12-07666-71910', '24-07686-82933', '22-07703-49186']},
                'OrderRole': 'Seller',
                # 'OrderStatus': 'Active'
            }
        )
        time = response.dict()['Timestamp']
        order_dict = response.dict()['OrderArray']
        order_array = order_dict['Order']

        for order in order_array:
            self.handle_object(self.import_direction, lambda obj_info: self.import_order(order, obj_info) )
