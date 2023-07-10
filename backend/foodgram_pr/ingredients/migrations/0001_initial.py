# Generated by Django 2.2.28 on 2022-05-04 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название ингредиента', max_length=200, unique=True, verbose_name='Название ингредиента')),
                ('measurement_unit', models.CharField(help_text='Единица измерения ингредиента', max_length=10, verbose_name='Единица измерения ингредиента')),
            ],
            options={
                'verbose_name': 'ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
    ]