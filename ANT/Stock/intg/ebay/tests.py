from unittest import TestCase
from xml.etree import ElementTree

from ebaysdk.trading import Connection as Trading

from cor.exception.app_exception import AppException
#from intg.ebay.ebayIntegrator import EbayIntegrator

#from intg.cfg.cfgModels import IntgCircuit

class TestEbay(TestCase):
    def print_order(self, order):
        print('--------------------')
        print(order['OrderID'])
        print('--------------------')

        for key in order:
            if key == 'CheckoutStatus' or key == 'ShippingDetails' or key == 'ShippingAddress' \
                    or key == 'ShippingServiceSelected':
                print(key + ':')
                for subKey in order[key]:
                    print('  ' + subKey + ': ' + str(order[key][subKey]))
            elif key == 'TransactionArray':
                print(key + ':')
                for trans in order[key]['Transaction']:
                    print('  new_trans:')
                    for subKey in trans:
                        print('    ' + subKey + ': ' + str(trans[subKey]))
                    print('  ' + str(trans))
            else:
                print(key + ': ' + str(order[key]))

    def _get_sandox_token(self):
        f = open("C:\Git\ANT\Stock\intg\ebay\ebay_token_sandbox.txt", "r")
        return f.read()

    def _get_prod_token(self):
        f = open("C:\Git\ANT\Stock\intg\ebay\ebay_token.txt", "r")
        return f.read()

    def get_token(self):
        return self._get_prod_token()

    def get_response_xml(self):
        f = open("C:\Git\ANT\Stock\intg\ebay\order_response_example.xml", "r")
        return f.read()

    def otest_get_token(self):
        print(self.get_token())

    def test_connect(self):
        #api = Trading(domain='api.sandbox.ebay.com',
        #              appid="AlekseyK-svarogmn-SBX-a23495a34-656da854", devid="897bd038-a619-4206-b7eb-c2ca642b4b37",
        #              certid="SBX-23495a34b3cd-991c-4300-9fc2-8def", token=self.get_token(), config_file=None)

        api = Trading(domain='api.ebay.com',
                      appid="AlekseyK-svarogmn-PRD-2a292be01-16024d26", devid="897bd038-a619-4206-b7eb-c2ca642b4b37",
                      certid="PRD-a292be012d9f-eb3b-418a-ba77-f0cc", token=self.get_token(), config_file=None)

        response = api.execute(
            'GetOrders',
            {
                #'CreateTimeFrom': '2021-10-01T00:05:08.100Z',
                #'CreateTimeTo': '2021-10-30T18:05:08.100Z',
                'OrderIDArray': {'OrderID': ['12-07666-71910', '24-07686-82933', '22-07703-49186']},
                'OrderRole': 'Seller',
                #'OrderStatus': 'Active'
            }
        )
        time = response.dict()['Timestamp']
        order_dict = response.dict()['OrderArray']
        order_array = order_dict['Order']

        #PaidTime: 2021-10-08T02:13:41.000Z - oplachen
        #ShippedTime: 2021-10-08T07:24:02.000Z - dostavlen

        for order in order_array:
            # self.print_order(order)

            # ИД заказа
            order_id = order.get('OrderID')
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
                    item_id = item.get('ItemID')
                    sku = item.get('SKU')
                    title = item.get('Title')
                    qty = int(trans.get('QuantityPurchased'))

                    if not sku:
                        raise AppException('Для товара ' + title + 'не указан SKU')

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

    def test_run_integrator(self):
        #intg = EbayIntegrator()
        #circuit = IntgCircuit.objects.filter(s_type=IntgCircuit.TYPE_EBAY).first()
        #intg.run(circuit)
        pass








