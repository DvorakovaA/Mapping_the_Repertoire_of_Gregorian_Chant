# Generated by Django 5.0 on 2024-01-02 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Map_repertoire', '0005_alter_geography_latitude_alter_geography_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='sources',
            name='num_century',
            field=models.IntegerField(null=True, verbose_name='num_century'),
        ),
    ]
