import re

USERNAME_VALID_PATTERN = r'[\w.@+-]'

username = '++++++???????'


"""Валидация поля username."""
# invalid_characters = re.sub(f'[^{USERNAME_VALID_PATTERN}]', '', username)
# if invalid_characters:
#     print(
#         f'В username найдены недопустимые символы: {", ".join(invalid_characters)}'
#     )

invalid_characters1 = re.sub(USERNAME_VALID_PATTERN, '', username)
if invalid_characters1:
    print(
        f'В username найдены недопустимые символы '
        f'{"".join(invalid_characters1)}'
    )