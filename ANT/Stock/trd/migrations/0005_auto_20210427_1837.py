# Generated by Django 2.2.6 on 2021-04-27 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trd', '0004_auto_20210425_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trdorder',
            name='id_trade_system',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='trd.TrdTradeSystem', verbose_name='Торговая система'),
        ),
    ]