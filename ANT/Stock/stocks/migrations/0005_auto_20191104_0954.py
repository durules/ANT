# Generated by Django 2.2.6 on 2019-11-04 04:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0004_auto_20191017_1428'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stkact',
            options={'verbose_name': 'Накладная', 'verbose_name_plural': 'Накладные'},
        ),
        migrations.AlterModelOptions(
            name='stkactdet',
            options={'verbose_name': 'Позиция накладной', 'verbose_name_plural': 'Позиции накладной'},
        ),
        migrations.AlterModelOptions(
            name='stkremains',
            options={'verbose_name': 'Остатки', 'verbose_name_plural': 'Остатки'},
        ),
    ]
