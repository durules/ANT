from unittest import TestCase
from xml.etree import ElementTree

from ebaysdk.trading import Connection as Trading


class TestEbay(TestCase):
    def get_token(self):
        f = open("C:\Git\ANT\Stock\intg\ebay\ebay_token.txt", "r")
        return f.read()

    def get_response_xml(self):
        f = open("C:\Git\ANT\Stock\intg\ebay\order_response_example.xml", "r")
        return f.read()

    def test_get_token(self):
        print(self.get_token())

    def test_connect(self):
        api = Trading(domain='api.sandbox.ebay.com',
                      appid="AlekseyK-svarogmn-SBX-a23495a34-656da854", devid="897bd038-a619-4206-b7eb-c2ca642b4b37", certid="SBX-23495a34b3cd-991c-4300-9fc2-8def", token=self.get_token(), config_file=None)
        response = api.execute('GetOrders', {'NumberOfDays': 30})
        print(response.dict())
        print(response.reply)

    def test_parse_response_xml(self):
        s_xml = self.get_response_xml()
        root = ElementTree.fromstring(s_xml)
        namespaces = {'xmlns': 'urn:ebay:apis:eBLBaseComponents'}
        order_array = root.find('xmlns:OrderArray', namespaces)
        for xml_order in order_array.findall('xmlns:Order', namespaces):
            print(xml_order.find('xmlns:OrderID', namespaces).text)
            # проверка на Completed, на всякий случай. По идее в запросе заказов они должны отфильтроваться
            print(xml_order.find('xmlns:OrderStatus', namespaces).text)





