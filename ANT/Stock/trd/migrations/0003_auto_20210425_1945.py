# Generated by Django 2.2.6 on 2021-04-25 14:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0006_stkact_s_desc'),
        ('goods', '0003_gdsgoodremainslevel'),
        ('trd', '0002_trdorder_trdorderstate_trdorderstatelevel'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trdtradesystem',
            options={'ordering': ['s_caption'], 'verbose_name': 'Торговая система', 'verbose_name_plural': 'Торговые системы'},
        ),
        migrations.AddField(
            model_name='trdorder',
            name='id_act_out',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='stocks.StkAct', verbose_name='Расходная накладная'),
        ),
        migrations.CreateModel(
            name='TrdOrderStateHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('d_date', models.DateTimeField(verbose_name='Дата')),
                ('s_user', models.CharField(max_length=256, verbose_name='Пользователь')),
                ('id_state_from', models.BigIntegerField(verbose_name='Состояние из')),
                ('id_state_to', models.BigIntegerField(verbose_name='Состояние в')),
                ('id_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trd.TrdOrder', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'История состояний заказа',
                'verbose_name_plural': 'Истории состояний заказа',
            },
        ),
        migrations.CreateModel(
            name='TrdOrderDet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_qty', models.BigIntegerField(verbose_name='Количество')),
                ('id_good', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='goods.GdsGood', verbose_name='Тмц')),
                ('id_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trd.TrdOrder', verbose_name='Накладная')),
            ],
            options={
                'verbose_name': 'Позиция заказа',
                'verbose_name_plural': 'Позиции заказа',
                'unique_together': {('id_order', 'id_good')},
            },
        ),
    ]
