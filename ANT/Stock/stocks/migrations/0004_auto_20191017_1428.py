# Generated by Django 2.2.6 on 2019-10-17 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0003_auto_20191008_1103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stkactdet',
            name='n_order',
        ),
        migrations.AlterField(
            model_name='stkact',
            name='d_reg_date',
            field=models.DateTimeField(null=True, verbose_name='Дата проведения'),
        ),
    ]
