from django.shortcuts import render

from goods.models import GdsGood
from stocks.models import StkRemains


def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """

    # Отображение остатков каждой тмц
    goods = GdsGood.objects.all()
    remains_by_good_dict = StkRemains.get_remains()

    result_dict = {}

    for good in goods:
        result_dict[good.id] = (good.sCaption, remains_by_good_dict.get(good.id, 0))

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'index.html',
        context={'remains_list': result_dict.values()},
    )
