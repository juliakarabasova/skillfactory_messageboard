from django import template
from string import punctuation

register = template.Library()


BAD_WORDS = ['слово', 'помело', 'производители', 'хозяев']


# Регистрируем наш фильтр под именем currency, чтоб Django понимал,
# что это именно фильтр для шаблонов, а не простая функция.
@register.filter()
def censor(value):
    if not isinstance(value, str):
        raise TypeError('Фильтр нужно применять к строкам')
    value = ' '.join([w if w.strip(punctuation).lower() not in BAD_WORDS else correct_word(w)
                      for w in value.split()])
    return value


@register.filter()
def to_string(value):
    return 'Новость' if value == 1 else 'Статья'


@register.filter()
def check_categories(value):
    print(value, value.__dict__)
    return value


def correct_word(word):
    new_w = ''
    first = True
    for letter in word:
        if letter in punctuation:       # Сохраняем все знаки пунктуации
            new_w += letter
        elif first:                     # Оставляем первую букву
            new_w += letter
            first = False
        else:
            new_w += '*'
    return new_w
