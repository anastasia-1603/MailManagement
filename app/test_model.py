
from transliterate import translit, get_available_language_codes

categ_flag_dict = {"вопросы": "VOPROSY", "готово к публикации": "GOTOVO_K_PUBLIKATSII",
              "доработка": "DORABOTKA", "другое": "DRUGOE",
              "отклонена": "OTKLONENA", "подача статьи": "PODACHA_STAT'I",
              "проверка статьи": "PROVERKA_STAT'I", "рецензирование": "RETSENZIROVANIE"}


def get_categ_by_flag(flag):
    return list(categ_flag_dict.keys())[list(categ_flag_dict.values()).index(flag)]

# print(get_categ_by_flag(';VOPROSY'))
print('VOPROSY' in categ_flag_dict.values())
#
# categories = ["Вопросы", "Готово к публикации",
#                   "Доработка", "Другое", "Отклонена",
#                   "Подача статьи", "Проверка статьи", "Рецензирование"]
# flags = []
# for c in categories:
#     flag = translit(c, 'ru', reversed=True)
#     flag = '_'.join(flag.split())
#     flags.append(flag.upper())
#     print(flag)
#     # tr = translit(flag, 'ru')
#     # print(tr)
#     # print()
# print(flags)

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
