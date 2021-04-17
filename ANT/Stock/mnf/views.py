from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from goods.models import GdsGood
from stocks.models import StkRemains


@login_required
def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """

    # Отображение остатков каждой тмц
    goods = GdsGood.objects.all()

    remains_by_good_dict = StkRemains.get_remains()

    result_dict = {}

    remains_count = 0
    for good in goods:
        n_qty = remains_by_good_dict.get(good.id, 0)
        color = good.get_remains_level(n_qty)
        result_dict[good.id] = (good.sCaption, n_qty, color)
        remains_count = remains_count + 1

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'index.html',
        context={'remains_list': result_dict.values(), 'canvas_height': remains_count * 11},
    )
