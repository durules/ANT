"""
Отчет по заказам.
Позволяет проаналзировать заказы в порядке их приоритета.
Получить информацию о наличии требуемых товаров на складе,
а так же необходимые материалы для производства товаров,
указанных в заказах
"""
from mnf.item.itemModels import MnfItem, MnfItemDet
from stocks.models import StkRemains
from trd.order.orderModels import TrdOrder, TrdOrderState, TrdOrderDet
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def build_report(request):
    """
    Построение отчета.
    """
    row_list_by_level_dict = {}

    # запрашиваем остатки товарам
    id_good_remain_dict = {}
    for remain in StkRemains.objects.all():
        id_good_remain_dict[remain.idGood_id] = remain.nQty

    # копируем, что вычислилть расход по исходным данным
    id_good_remain_dict_old = id_good_remain_dict.copy()

    # Берем заказы
    for order in TrdOrder.objects.filter(id_state__n_order__lt=TrdOrderState.get_write_off_state_number()).order_by('-d_reg_date'):
        order_det_list = []

        order_state_level = order.get_level_by_state()
        # определяем приоритет заказа
        n_order_priority = -1
        if order_state_level is not None:
            n_order_priority = order_state_level.id_level.n_level

        # определяем цвет
        s_order_color = None
        if order_state_level is not None:
            s_order_color = order_state_level.get_color()

        # собираем позиции
        for order_det in TrdOrderDet.objects.filter(id_order=order):
            order_det_list.append(order_det)

        row = (order, s_order_color, order_det_list)
        if n_order_priority not in row_list_by_level_dict:
            row_list_by_level_dict[n_order_priority] = []

        row_list_by_level_dict[n_order_priority].append(row)

    # Собираем список строк
    row_list = []
    priority_list = list(row_list_by_level_dict.keys())
    priority_list.sort()
    priority_list.reverse()

    # перечень требуемых ТМЦ
    good_req_set = set()
    mat_req_set = set()

    for n_priority in priority_list:
        for order, s_order_color, order_det_list in row_list_by_level_dict[n_priority]:
            # определяем наличие требуемых ТМЦ
            has_goods = True
            has_materials = True

            # количество недостающих товаров по заказу
            good_by_order_req_dict = {}

            for order_det in order_det_list:
                id_good_remain_dict[order_det.id_good_id] = id_good_remain_dict[order_det.id_good_id] - order_det.n_qty

                # признак, что есть остатки на складе
                is_has_good_remains = id_good_remain_dict[order_det.id_good_id] >= 0

                if not is_has_good_remains:
                    has_goods = False

                    if id_good_remain_dict[order_det.id_good_id] * -1 > order_det.n_qty:
                        good_by_order_req_dict[order_det.id_good] = order_det.n_qty
                    else:
                        good_by_order_req_dict[order_det.id_good] = id_good_remain_dict[order_det.id_good_id] * -1

                    good_req_set.add(order_det.id_good)

                    # определяем наличие материалов
                    mnf_item = MnfItem.objects.filter(id_good=order_det.id_good).first()

                    if mnf_item is not None:
                        for item_det in MnfItemDet.objects.filter(id_item=mnf_item):
                            id_good_remain_dict[item_det.id_good_id] = id_good_remain_dict[
                                                                            item_det.id_good_id] - item_det.n_qty
                            is_has_mat_remains = id_good_remain_dict[item_det.id_good_id] >= 0
                            if not is_has_mat_remains:
                                has_materials = False
                                mat_req_set.add(item_det.id_good)

            if has_goods:
                has_materials = True

            row_list.append((order, s_order_color, has_goods, has_materials, good_by_order_req_dict, order_det_list))

    good_req_dict = {}
    for good in good_req_set:
        good_req_dict[good] = abs(id_good_remain_dict_old[good.id] - id_good_remain_dict[good.id])

    mat_req_dict = {}
    for good in mat_req_set:
        mat_req_dict[good] = abs(id_good_remain_dict_old[good.id] - id_good_remain_dict[good.id])

    return render(
        request,
        'stock/trd/trd_order_report.html',
        context={'row_list': row_list, 'good_req_dict': good_req_dict, 'mat_req_dict': mat_req_dict},
    )