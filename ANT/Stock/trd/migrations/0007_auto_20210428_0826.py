# Generated by Django 2.2.6 on 2021-04-28 03:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trd', '0006_auto_20210427_2150'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrdDeliveryService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('s_caption', models.CharField(max_length=256, verbose_name='Наименование')),
            ],
            options={
                'verbose_name': 'Служба доставки',
                'verbose_name_plural': 'Службы доставки',
                'ordering': ['s_caption'],
            },
        ),
        migrations.AddField(
            model_name='trdorder',
            name='s_address',
            field=models.CharField(blank=True, max_length=4000, null=True, verbose_name='Адрес'),
        ),
        migrations.AddField(
            model_name='trdorder',
            name='s_receiver',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Получатель'),
        ),
        migrations.AddField(
            model_name='trdorder',
            name='s_reg_num',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Номер'),
        ),
        migrations.AddField(
            model_name='trdorder',
            name='s_track_num',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Трек-номер'),
        ),
        migrations.AddField(
            model_name='trdorder',
            name='id_delivery_service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='trd.TrdDeliveryService', verbose_name='Служба доставки'),
        ),
    ]
