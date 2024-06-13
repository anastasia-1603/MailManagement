
from transliterate import translit, get_available_language_codes


categories = ["Вопросы", "Готово к публикации",
                  "Доработка", "Другое", "Отклонена",
                  "Подача статьи", "Проверка статьи", "Рецензирование"]
flags = []
for c in categories:
    flag = translit(c, 'ru', reversed=True)
    flag = '_'.join(flag.split())
    flags.append(flag.upper())
    print(flag)
    # tr = translit(flag, 'ru')
    # print(tr)
    # print()
print(flags)

# Voprosy
# Вопросы
# Gotovo_k_publikatsii
# Готово_к_публикации
# Dorabotka
# Доработка
# Drugoe
# Другое
# Otklonena
# Отклонена
# Podacha_stat'i
# Подача_статЬи
# Proverka_stat'i
# Проверка_статЬи
# Retsenzirovanie
# Рецензирование
