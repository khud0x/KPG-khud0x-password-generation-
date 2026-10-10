#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wordlist generatsiya mantig'i — leetspeak, katta/kichik harf, yil,
maxsus belgi va bo'limlarni juftlashtirish orqali parollar ro'yxatini quradi.
"""

import os
import itertools

# ----------------------------------------------------------------------
# Transformatsiya sozlamalari
# ----------------------------------------------------------------------

LEET_MAP = {
    "a": "4", "A": "4",
    "e": "3", "E": "3",
    "i": "1", "I": "1",
    "o": "0", "O": "0",
    "s": "5", "S": "5",
    "t": "7", "T": "7",
    "b": "8", "B": "8",
}

SPECIAL_CHARS = ["!", "@", "#", "$", "_", "-", "*", "."]
NUMBER_SUFFIXES = [str(n) for n in range(0, 100)] + [
    "123", "007", "321", "111", "000", "999"
]

DEFAULT_PROFILE_PATH = os.path.join(os.path.expanduser("~"), ".wordlist_gen_profile.json")


def leetspeak(word: str) -> str:
    return "".join(LEET_MAP.get(ch, ch) for ch in word)


def case_variants(word: str):
    variants = {word, word.lower(), word.upper(), word.capitalize()}
    return variants


def is_year(s: str) -> bool:
    return s.isdigit() and len(s) == 4 and 1900 <= int(s) <= 2035


# ----------------------------------------------------------------------
# Generatsiya mantig'i
# ----------------------------------------------------------------------

class GenerationCancelled(Exception):
    pass


def build_wordlist(categories: dict, min_len: int, max_len: int, options: dict,
                    max_results: int, progress_q: "queue.Queue", cancel_event):
    """
    categories: {category_name: [values,...]}
    options: dict of bool flags - case, leet, numbers, special, years, pairs
    Natija: set() — noyob so'zlar/parollar ro'yxati (min_len..max_len oralig'ida)
    """
    all_values = []
    for vals in categories.values():
        all_values.extend(v for v in vals if v.strip())

    base_words = set()
    for w in all_values:
        w = w.strip()
        if not w:
            continue
        base_words.add(w)
        if options.get("case"):
            base_words |= case_variants(w)
        if options.get("leet"):
            base_words.add(leetspeak(w))
            if options.get("case"):
                base_words.add(leetspeak(w.capitalize()))

    years = [v.strip() for v in all_values if is_year(v.strip())]

    results = set()
    total_base = len(base_words)
    processed = 0

    def add_if_valid(word):
        if min_len <= len(word) <= max_len:
            results.add(word)

    # 1) Yolg'iz so'zlar (sof holatda)
    for w in base_words:
        if cancel_event.is_set():
            raise GenerationCancelled()
        add_if_valid(w)
        processed += 1
        if processed % 200 == 0:
            progress_q.put(("progress", f"Asosiy so'zlar: {processed}/{total_base}"))
        if len(results) >= max_results:
            progress_q.put(("progress", "Maksimal natija soniga yetildi."))
            return results

    # 2) So'z + raqam
    if options.get("numbers"):
        for w in base_words:
            if cancel_event.is_set():
                raise GenerationCancelled()
            for suf in NUMBER_SUFFIXES:
                add_if_valid(w + suf)
                add_if_valid(suf + w)
                if len(results) >= max_results:
                    progress_q.put(("progress", "Maksimal natija soniga yetildi."))
                    return results

    # 3) So'z + maxsus belgi (+ ixtiyoriy raqam)
    if options.get("special"):
        for w in base_words:
            if cancel_event.is_set():
                raise GenerationCancelled()
            for sp in SPECIAL_CHARS:
                add_if_valid(w + sp)
                add_if_valid(sp + w)
                if options.get("numbers"):
                    for suf in ("1", "2", "123", "01"):
                        add_if_valid(w + sp + suf)
                if len(results) >= max_results:
                    progress_q.put(("progress", "Maksimal natija soniga yetildi."))
                    return results

    # 4) So'z + yil (agar kiritilgan yillar mavjud bo'lsa)
    if options.get("years") and years:
        for w in base_words:
            if cancel_event.is_set():
                raise GenerationCancelled()
            for y in years:
                add_if_valid(w + y)
                add_if_valid(y + w)
                add_if_valid(w + y[-2:])
                if len(results) >= max_results:
                    progress_q.put(("progress", "Maksimal natija soniga yetildi."))
                    return results

    # 5) Ikki bo'limdan juftlashtirish (masalan Ism+Familiya, Ism+Hayvon)
    if options.get("pairs"):
        cat_names = [c for c, vals in categories.items() if any(v.strip() for v in vals)]
        for c1, c2 in itertools.permutations(cat_names, 2):
            if cancel_event.is_set():
                raise GenerationCancelled()
            vals1 = [v.strip() for v in categories[c1] if v.strip()]
            vals2 = [v.strip() for v in categories[c2] if v.strip()]
            for v1 in vals1:
                for v2 in vals2:
                    add_if_valid(v1 + v2)
                    add_if_valid(v1 + "_" + v2)
                    if options.get("numbers"):
                        add_if_valid(v1 + v2 + "123")
                    if len(results) >= max_results:
                        progress_q.put(("progress", "Maksimal natija soniga yetildi."))
                        return results
            progress_q.put(("progress", f"Juftlashtirilmoqda: {c1} x {c2} ({len(results)} ta natija)"))

    return results
