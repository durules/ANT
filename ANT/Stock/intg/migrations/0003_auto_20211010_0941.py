# Generated by Django 2.2.6 on 2021-10-10 04:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('intg', '0002_auto_20211010_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intgcircuitruntimedata',
            name='id_circuit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='intg.IntgCircuit', verbose_name='Контур'),
        ),
    ]