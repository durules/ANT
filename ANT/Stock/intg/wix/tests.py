from unittest import TestCase
import requests

from cor.exception.app_exception import AppException

class TestWix(TestCase):

    def _get_prod_token(self):
        f = open("C:\Git\ANT\Stock\intg\wix\wix_token.txt", "r")
        return f.read()

    def get_token(self):
        return self._get_prod_token()


    def test_get_token(self):
        print(self.get_token())

    def test_connect(self):
        params = {'order_id_array': '11797;11796'}
        headers = {'secret': self.get_token()}
        response = requests.get(
            'https://www.svaroghunt.ru/_functions/orders',
            params=params,
            headers=headers
        )
        response.raise_for_status()

        response_json = response.json()

        time = response_json["date"]
        print(time)

        order_array = response_json['orders']
        if order_array:
            for order in order_array:
                # ИД заказа
                order_id = order.get('number')
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
                        shipping_address_name = str(shipment_details.get('lastName')) + ' ' + str(shipment_details.get('firstName'))
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

                print(order)
                print(order_id)
                print(is_payed)
                print(is_finished)
                print(created_time)
                print(shipping_address_name)
                print(shipping_address_address)
                print(shipment_tracking_number)
                print(selled_sku_list)
                print(delivery_option)










