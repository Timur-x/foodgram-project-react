from django.db.models import Model, CharField, UniqueConstraint


class Ingredient(Model):
    name = CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название',
    )
    measurement_unit = CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return self.name
