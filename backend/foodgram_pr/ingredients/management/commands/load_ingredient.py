import json

from django.core.management.base import BaseCommand
from django.db import transaction
from recipes.models import Ingredient


class Command(BaseCommand):
    help = ' Загрузить данные в модель ингредиентов '

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Старт команды'))
        with open('data/ingredients.json', encoding='utf-8',
                  ) as data_file_ingredients:
            ingredient_data = json.loads(data_file_ingredients.read())
            ingredients = [Ingredient(**ingr) for ingr in ingredient_data]
            Ingredient.objects.bulk_create(ingredients)
        self.stdout.write(self.style.SUCCESS('Все ингридиенты загружены!'))
