import html

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from cor.exception.app_exception import AppException
from intg.cfg.cfgModels import IntgCircuit
from intg.ebay.ebayIntegrator import EbayIntegrator
from intg.wix.wixIntegrator import WixIntegrator
from trd.order.orderModels import TrdOrder


@login_required
def run_order_integration(request):
    """Запуск интеграции по всем контурам"""
    has_errors = False
    error_text_lines = []

    for circuit in IntgCircuit.objects.all():
        integrator = None
        if circuit.s_type == IntgCircuit.TYPE_EBAY:
            integrator = EbayIntegrator()
        elif circuit.s_type == IntgCircuit.TYPE_Wix:
            integrator = WixIntegrator()
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

@login_required
def run_order_integration_by_id(request, pk):
    """Запуск интеграции по одному заказу"""
    trd_order = TrdOrder.objects.get(pk=pk)

    for circuit in IntgCircuit.objects.filter(id_trade_system=trd_order.id_trade_system):
        integrator = None
        if circuit.s_type == IntgCircuit.TYPE_EBAY:
            integrator = EbayIntegrator()
            integrator.run_by_single_order(trd_order.s_reg_num)
        else:
            raise AppException('Неизвестный тип контура: ' + circuit.s_type)

        if integrator.has_errors():
            # Переводим текст в html, чтобы норм отобразить
            return render(
                request,
                'show_text.html',
                context={'lines': integrator.get_report()},
            )
        else:
            return HttpResponseRedirect(reverse('trd_order-detail', args=[str(trd_order.id)]))

