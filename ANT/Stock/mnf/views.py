from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from mnf.material.materialModels import MnfMaterial
from stocks.models import StkRemains


@login_required
def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """

    # Отображение остатков каждой тмц
    materials = MnfMaterial.objects.all()

    remains_by_good_dict = StkRemains.get_remains()

    result_dict = {}

    remains_count = 0
    for material in materials:
        n_qty = remains_by_good_dict.get(material.id_good_id, 0)
        remains_level = material.get_remains_level(n_qty)
        result_dict[material.id] = (material.s_caption, n_qty, remains_level)
        remains_count = remains_count + 1

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'index.html',
        context={'remains_list': result_dict.values(), 'canvas_height': remains_count * 11},
    )
