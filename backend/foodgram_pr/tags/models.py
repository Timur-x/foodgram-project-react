from django.db.models import CharField, Model, SlugField


class Tag(Model):
    name = CharField('Название', max_length=200)
    color = CharField('Цвет в HEX', max_length=7)
    slug = SlugField('Уникальный слаг', max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
