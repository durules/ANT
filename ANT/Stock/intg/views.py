import html

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from cor.exception.app_exception import AppException
from intg.cfg.cfgModels import IntgCircuit
from intg.ebay.ebayIntegrator import EbayIntegrator


@login_required
def run_order_integration(request):
    """Запуск интеграции по всем контурам"""
    has_errors = False
    error_text_lines = []

    for circuit in IntgCircuit.objects.all():
        integrator = None
        if circuit.s_type == IntgCircuit.TYPE_EBAY:
            integrator = EbayIntegrator()
        else:
            raise AppException('Неизвестный тип контура: ' + circuit.s_type)

        integrator.run(circuit)

        # Собиаем информацию о выполненнии
        if integrator.has_errors():
            if not has_errors:
                has_errors = True
            error_text_lines = error_text_lines + integrator.get_report()

    if has_errors:
        # Переводим текст в html, чтобы норм отобразить
        return render(
            request,
            'show_text.html',
            context={'lines': error_text_lines},
        )
    else:
        return HttpResponseRedirect(reverse('trd_orders'))
