#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Virtual klaviatura uchun harf/raqam/maxsus belgi ma'lumotlari.
"""

# ----------------------------------------------------------------------
# Virtual klaviatura — harf tartiblari (4 til) + raqamlar + parol uchun
# ishlatiladigan barcha maxsus belgilar
# ----------------------------------------------------------------------

KEYBOARD_LETTER_ROWS = {
    # O'zbek lotin alifbosi — standart QWERTY + maxsus harflar (o', g', sh, ch)
    "uz": [
        list("qwertyuiop"),
        list("asdfghjkl"),
        list("zxcvbnm"),
        ["o'", "g'", "sh", "ch", "ng", "'"],
    ],
    # Tojik kirill alifbosi — ЙЦУКЕН asosida + tojikchaga xos harflar
    "tj": [
        list("йцукенгшщзхъ"),
        list("фывапролджэ"),
        list("ячсмитьбю"),
        list("ғӣқӯҳҷ"),
    ],
    # Rus kirill alifbosi — standart ЙЦУКЕН
    "ru": [
        list("йцукенгшщзхъ"),
        list("фывапролджэ"),
        list("ячсмитьбюё"),
    ],
    # Ingliz lotin alifbosi — standart QWERTY
    "en": [
        list("qwertyuiop"),
        list("asdfghjkl"),
        list("zxcvbnm"),
    ],
}

KEYBOARD_NUMBER_ROW = list("0123456789")

# Parollarda ishlatiladigan deyarli barcha maxsus belgilar (ASCII)
KEYBOARD_SPECIAL_CHARS = list("!@#$%^&*()-_=+[]{};:'\",.<>/?\\|~`")
