# Generated by Django 3.2.13 on 2022-11-28 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ltw_btl', '0006_alter_book_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='gender',
            field=models.CharField(choices=[(1, 'Nam'), (0, 'Nữ')], default=1, max_length=100, null=True),
        ),
    ]
