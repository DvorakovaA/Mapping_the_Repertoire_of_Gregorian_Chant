# Generated by Django 5.0 on 2024-01-01 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Map_repertoire', '0004_rename_id_feasts_feast_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geography',
            name='latitude',
            field=models.FloatField(null=True, verbose_name='latitude'),
        ),
        migrations.AlterField(
            model_name='geography',
            name='longitude',
            field=models.FloatField(null=True, verbose_name='longitude'),
        ),
    ]
