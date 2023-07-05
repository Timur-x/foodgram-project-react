from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from ingredients.models import Ingredient
from tags.models import Tag

TIME_MIN = 1

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        related_name='recipes',
        verbose_name='Список ингредиентов',
        help_text='Список ингредиентов',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(TIME_MIN),),
        verbose_name='Время приготовления (в минутах)',
        help_text='Время приготовления (в минутах)',
    )
    image = models.ImageField(
        verbose_name='Картинка, закодированная в Base64',
        help_text='Картинка, закодированная в Base64',
        upload_to='recipes/',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTags',
        related_name='recipes',
        verbose_name='Список id тегов',
        help_text='Список id тегов',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепты'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'В рецепте {self.recipe} есть ингредиент {self.ingredient}'


class RecipeTags(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )

    class Meta:
        verbose_name = 'теги'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'У рецепта {self.recipe} есть тег {self.tag}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorite',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            ),
        )

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class CountOfIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='count_in_recipes',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'amount',),
                name='unique_ingredient_amount',
            ),
        )

    def __str__(self):
        return (
            f'{self.ingredient.name} - {self.amount}'
            f' ({self.ingredient.measurement_unit})'
        )
