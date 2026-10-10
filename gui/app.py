#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grafik interfeys (WordlistApp) — barcha oynalar, tugmalar va
virtual klaviatura shu yerda. Mantiq core/, matnlar i18n/ ichida.
"""

import json
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.wordlist_logic import build_wordlist, GenerationCancelled
from i18n.strings import LANGS, LANG_NAMES, STRINGS, DEFAULT_CATEGORY_NAMES
from gui.keyboard_data import KEYBOARD_LETTER_ROWS, KEYBOARD_NUMBER_ROW, KEYBOARD_SPECIAL_CHARS


# ----------------------------------------------------------------------
# GUI
# ----------------------------------------------------------------------

class WordlistApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = "uz"
        self.geometry("1000x640")
        self.minsize(880, 580)

        self.categories = {}   # {name: [values]}
        self.cancel_event = threading.Event()
        self.progress_q = queue.Queue()
        self.gen_thread = None
        self._last_results = []
        self._progress_pending_key = None  # ("pairing", c1, c2, n) or ("max_reached",) for live status

        self.active_entry = None       # tk.Entry widget currently receiving virtual-keyboard input
        self.keyboard_window = None    # Toplevel holding the virtual keyboard
        self.vk_shift = False
        self.vk_letter_buttons = []    # list of (button, lower_char) for live-updating on shift toggle

        self._build_ui()
        self._load_default_categories()
        self._apply_language()

        # Butun dastur bo'yicha: istalgan matn maydoniga fokus tushganda,
        # o'sha maydon virtual klaviaturaning "nishoni" bo'lib qoladi
        # (shu jumladan dialog oynalaridagi maydonlar ham).
        self.bind_class("Entry", "<FocusIn>", self._on_any_entry_focus)
        self.bind_class("TEntry", "<FocusIn>", self._on_any_entry_focus)

    def t(self, key, **kwargs):
        s = STRINGS[self.lang].get(key, STRINGS["uz"].get(key, key))
        return s.format(**kwargs) if kwargs else s

    def _on_any_entry_focus(self, event):
        widget = event.widget
        if isinstance(widget, (tk.Entry, ttk.Entry)):
            self.active_entry = widget

    # ---------------- Tarjima qilinadigan universal dialog oynalar ----------------
    # (standart tkinter messagebox/simpledialog o'z tugmalarini — OK/Cancel/Yes/No —
    # tilga moslab bo'lmaydi, shu sabab o'zimizning dialoglarimiz ishlatiladi)
    def _custom_dialog(self, title, message, buttons):
        result = {"value": None}
        win = tk.Toplevel(self)
        win.title(title)
        win.transient(self)
        # Modal grab ataylab qo'yilmagan: grab_set() butun dastur bo'yicha
        # barcha boshqa oynalarni (jumladan Virtual klaviaturani) bloklab
        # qo'yardi va ular bilan bir vaqtda ishlash imkonsiz bo'lib qolardi.
        win.resizable(False, False)
        win.lift()
        win.focus_force()

        ttk.Label(win, text=message, wraplength=360, justify="left").pack(padx=16, pady=16)

        btn_frame = ttk.Frame(win)
        btn_frame.pack(padx=16, pady=(0, 16))

        def make_cmd(key):
            def _cmd():
                result["value"] = key
                win.destroy()
            return _cmd

        for key, text in buttons:
            ttk.Button(btn_frame, text=text, command=make_cmd(key)).pack(side=tk.LEFT, padx=4)

        win.bind("<Escape>", lambda e: win.destroy())
        win.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - win.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.wait_window(win)
        return result["value"]

    def _info(self, title, message):
        self._custom_dialog(title, message, [("ok", self.t("dlg_ok_btn"))])

    def _warning(self, title, message):
        self._custom_dialog(title, message, [("ok", self.t("dlg_ok_btn"))])

    def _error(self, title, message):
        self._custom_dialog(title, message, [("ok", self.t("dlg_ok_btn"))])

    def _yesno(self, title, message):
        res = self._custom_dialog(title, message, [
            ("yes", self.t("dlg_yes_btn")),
            ("no", self.t("dlg_no_btn")),
        ])
        return res == "yes"

    def _ask_string(self, title, prompt):
        result = {"value": None}
        win = tk.Toplevel(self)
        win.title(title)
        win.transient(self)
        # Modal grab ataylab qo'yilmagan — aks holda Virtual klaviatura oynasi
        # bu dialog ochiq turganda hech qanday bosishga javob bermay qolardi.
        win.resizable(False, False)
        win.lift()
        win.focus_force()

        ttk.Label(win, text=prompt, wraplength=360, justify="left").pack(padx=16, pady=(16, 8), anchor="w")
        entry = ttk.Entry(win, width=40)
        entry.pack(padx=16, pady=(0, 12), fill=tk.X)
        entry.focus_set()

        btns = ttk.Frame(win)
        btns.pack(padx=16, pady=(0, 16))

        def on_ok(event=None):
            result["value"] = entry.get()
            win.destroy()

        def on_cancel(event=None):
            result["value"] = None
            win.destroy()

        ttk.Button(btns, text=self.t("dlg_ok_btn"), command=on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text=self.t("dlg_cancel_btn"), command=on_cancel).pack(side=tk.LEFT, padx=4)

        entry.bind("<Return>", on_ok)
        win.bind("<Escape>", on_cancel)

        win.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - win.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{max(x, 0)}+{max(y, 0)}")

        self.wait_window(win)
        return result["value"]

    # ---------------- UI qurish ----------------
    def _build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=8, pady=(8, 0))
        self.brand_title_lbl = ttk.Label(header, font=("Segoe UI", 15, "bold"))
        self.brand_title_lbl.pack(anchor="center")

        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=(4, 0))
        self.lang_label_widget = ttk.Label(top, text="Til:")
        self.lang_label_widget.pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value=LANG_NAMES[self.lang])
        self.lang_combo = ttk.Combobox(top, textvariable=self.lang_var, state="readonly",
                                        values=[LANG_NAMES[c] for c in LANGS], width=14)
        self.lang_combo.pack(side=tk.LEFT, padx=6)
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        main = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Chap panel
        left = ttk.Frame(main)
        main.add(left, weight=1)

        self.categories_header_lbl = ttk.Label(left, font=("Segoe UI", 11, "bold"))
        self.categories_header_lbl.pack(anchor="w")

        cat_frame = ttk.Frame(left)
        cat_frame.pack(fill=tk.X, pady=4)
        self.cat_listbox = tk.Listbox(cat_frame, height=8, exportselection=False)
        self.cat_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.cat_listbox.bind("<<ListboxSelect>>", self._on_select_category)
        cat_scroll = ttk.Scrollbar(cat_frame, orient=tk.VERTICAL, command=self.cat_listbox.yview)
        cat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.cat_listbox.config(yscrollcommand=cat_scroll.set)

        cat_btns = ttk.Frame(left)
        cat_btns.pack(fill=tk.X, pady=2)
        self.add_category_btn = ttk.Button(cat_btns, command=self._add_category)
        self.add_category_btn.pack(side=tk.LEFT, padx=2)
        self.delete_category_btn = ttk.Button(cat_btns, command=self._delete_category)
        self.delete_category_btn.pack(side=tk.LEFT, padx=2)

        ttk.Separator(left).pack(fill=tk.X, pady=8)

        self.values_header_lbl = ttk.Label(left, font=("Segoe UI", 11, "bold"))
        self.values_header_lbl.pack(anchor="w")
        self.values_label = ttk.Label(left, foreground="#666")
        self.values_label.pack(anchor="w", pady=(0, 4))

        val_frame = ttk.Frame(left)
        val_frame.pack(fill=tk.BOTH, expand=True, pady=4)
        self.val_listbox = tk.Listbox(val_frame, exportselection=False)
        self.val_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        val_scroll = ttk.Scrollbar(val_frame, orient=tk.VERTICAL, command=self.val_listbox.yview)
        val_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.val_listbox.config(yscrollcommand=val_scroll.set)

        add_val_frame = ttk.Frame(left)
        add_val_frame.pack(fill=tk.X, pady=4)
        self.val_entry = ttk.Entry(add_val_frame)
        self.val_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.val_entry.bind("<Return>", lambda e: self._add_value())
        self.val_entry.bind("<FocusIn>", lambda e: self._set_active_entry(self.val_entry))
        self.add_value_btn = ttk.Button(add_val_frame, command=self._add_value)
        self.add_value_btn.pack(side=tk.LEFT)
        self.delete_value_btn = ttk.Button(add_val_frame, command=self._delete_value)
        self.delete_value_btn.pack(side=tk.LEFT, padx=(4, 0))
        self.keyboard_btn = ttk.Button(add_val_frame, command=self._toggle_keyboard)
        self.keyboard_btn.pack(side=tk.LEFT, padx=(4, 0))

        profile_btns = ttk.Frame(left)
        profile_btns.pack(fill=tk.X, pady=(8, 0))
        self.save_profile_btn = ttk.Button(profile_btns, command=self._save_profile)
        self.save_profile_btn.pack(side=tk.LEFT, padx=2)
        self.load_profile_btn = ttk.Button(profile_btns, command=self._load_profile)
        self.load_profile_btn.pack(side=tk.LEFT, padx=2)

        # O'ng panel
        right = ttk.Frame(main)
        main.add(right, weight=1)

        self.settings_header_lbl = ttk.Label(right, font=("Segoe UI", 11, "bold"))
        self.settings_header_lbl.pack(anchor="w")

        len_frame = ttk.Frame(right)
        len_frame.pack(fill=tk.X, pady=6)
        self.min_len_lbl = ttk.Label(len_frame)
        self.min_len_lbl.grid(row=0, column=0, sticky="w")
        self.min_len_var = tk.IntVar(value=4)
        ttk.Spinbox(len_frame, from_=4, to=16, textvariable=self.min_len_var, width=5).grid(row=0, column=1, padx=6)
        self.max_len_lbl = ttk.Label(len_frame)
        self.max_len_lbl.grid(row=0, column=2, sticky="w", padx=(12, 0))
        self.max_len_var = tk.IntVar(value=16)
        ttk.Spinbox(len_frame, from_=4, to=16, textvariable=self.max_len_var, width=5).grid(row=0, column=3, padx=6)

        self.opt_frame = ttk.LabelFrame(right)
        self.opt_frame.pack(fill=tk.X, pady=8)
        self.opt_case = tk.BooleanVar(value=True)
        self.opt_leet = tk.BooleanVar(value=True)
        self.opt_numbers = tk.BooleanVar(value=True)
        self.opt_special = tk.BooleanVar(value=True)
        self.opt_years = tk.BooleanVar(value=True)
        self.opt_pairs = tk.BooleanVar(value=True)
        # Eslatma: ttk.Checkbutton ba'zi tizim mavzularida belgilanganda butun
        # katakchani rangga bo'yab yuboradi. Shu sababli bu yerda klassik
        # tk.Checkbutton ishlatiladi — u har doim oddiy katakcha + ✓ belgisi
        # ko'rinishida bo'ladi, fon rangi o'zgarmaydi.
        cb_kwargs = dict(anchor="w", padx=6, pady=2)
        self.opt_case_cb = tk.Checkbutton(self.opt_frame, variable=self.opt_case, **cb_kwargs)
        self.opt_case_cb.grid(row=0, column=0, sticky="w", padx=6, pady=2)
        self.opt_leet_cb = tk.Checkbutton(self.opt_frame, variable=self.opt_leet, **cb_kwargs)
        self.opt_leet_cb.grid(row=0, column=1, sticky="w", padx=6, pady=2)
        self.opt_numbers_cb = tk.Checkbutton(self.opt_frame, variable=self.opt_numbers, **cb_kwargs)
        self.opt_numbers_cb.grid(row=1, column=0, sticky="w", padx=6, pady=2)
        self.opt_special_cb = tk.Checkbutton(self.opt_frame, variable=self.opt_special, **cb_kwargs)
        self.opt_special_cb.grid(row=1, column=1, sticky="w", padx=6, pady=2)
        self.opt_years_cb = tk.Checkbutton(self.opt_frame, variable=self.opt_years, **cb_kwargs)
        self.opt_years_cb.grid(row=2, column=0, sticky="w", padx=6, pady=2)
        self.opt_pairs_cb = tk.Checkbutton(self.opt_frame, variable=self.opt_pairs, **cb_kwargs)
        self.opt_pairs_cb.grid(row=2, column=1, sticky="w", padx=6, pady=2)

        limit_frame = ttk.Frame(right)
        limit_frame.pack(fill=tk.X, pady=4)
        self.max_results_lbl = ttk.Label(limit_frame)
        self.max_results_lbl.pack(side=tk.LEFT)
        self.max_results_var = tk.IntVar(value=200000)
        ttk.Spinbox(limit_frame, from_=1000, to=5000000, increment=1000,
                    textvariable=self.max_results_var, width=10).pack(side=tk.LEFT, padx=6)

        gen_frame = ttk.Frame(right)
        gen_frame.pack(fill=tk.X, pady=10)
        self.generate_btn = ttk.Button(gen_frame, command=self._start_generation)
        self.generate_btn.pack(side=tk.LEFT)
        self.cancel_btn = ttk.Button(gen_frame, command=self._cancel_generation, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=6)

        self.status_var = tk.StringVar()
        ttk.Label(right, textvariable=self.status_var, foreground="#444").pack(anchor="w", pady=(0, 4))
        self.progress = ttk.Progressbar(right, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(0, 8))

        self.results_header_lbl = ttk.Label(right, font=("Segoe UI", 11, "bold"))
        self.results_header_lbl.pack(anchor="w")
        res_frame = ttk.Frame(right)
        res_frame.pack(fill=tk.BOTH, expand=True, pady=4)
        self.result_listbox = tk.Listbox(res_frame)
        self.result_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        res_scroll = ttk.Scrollbar(res_frame, orient=tk.VERTICAL, command=self.result_listbox.yview)
        res_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_listbox.config(yscrollcommand=res_scroll.set)

        result_btns = ttk.Frame(right)
        result_btns.pack(fill=tk.X, pady=4)
        self.clear_results_btn = ttk.Button(result_btns, command=self._clear_results, state=tk.DISABLED)
        self.clear_results_btn.pack(side=tk.RIGHT, padx=(4, 0))
        self.save_result_btn = ttk.Button(result_btns, command=self._save_results, state=tk.DISABLED)
        self.save_result_btn.pack(side=tk.RIGHT)

    # ---------------- Til almashtirish ----------------
    def _on_language_change(self, event=None):
        selected_name = self.lang_var.get()
        for code, name in LANG_NAMES.items():
            if name == selected_name:
                self.lang = code
                break
        self._apply_language()

    def _apply_language(self):
        self.title(self.t("brand_title"))
        self.brand_title_lbl.config(text=self.t("brand_title"))
        self.lang_label_widget.config(text=self.t("lang_label"))

        self.categories_header_lbl.config(text=self.t("categories_header"))
        self.add_category_btn.config(text=self.t("add_category_btn"))
        self.delete_category_btn.config(text=self.t("delete_category_btn"))

        self.values_header_lbl.config(text=self.t("values_header"))
        name = self._current_category()
        if name is None:
            self.values_label.config(text=self.t("no_category_selected"))
        else:
            self.values_label.config(text=self.t("values_label_fmt", name=name, count=len(self.categories[name])))

        self.add_value_btn.config(text=self.t("add_btn"))
        self.delete_value_btn.config(text=self.t("delete_value_btn"))
        self.keyboard_btn.config(text=self.t("keyboard_btn"))
        self.save_profile_btn.config(text=self.t("save_profile_btn"))
        self.load_profile_btn.config(text=self.t("load_profile_btn"))

        self.settings_header_lbl.config(text=self.t("settings_header"))
        self.min_len_lbl.config(text=self.t("min_len"))
        self.max_len_lbl.config(text=self.t("max_len"))

        self.opt_frame.config(text=self.t("options_header"))
        self.opt_case_cb.config(text=self.t("opt_case"))
        self.opt_leet_cb.config(text=self.t("opt_leet"))
        self.opt_numbers_cb.config(text=self.t("opt_numbers"))
        self.opt_special_cb.config(text=self.t("opt_special"))
        self.opt_years_cb.config(text=self.t("opt_years"))
        self.opt_pairs_cb.config(text=self.t("opt_pairs"))

        self.max_results_lbl.config(text=self.t("max_results"))
        self.generate_btn.config(text=self.t("generate_btn"))
        self.cancel_btn.config(text=self.t("cancel_btn"))
        if not self.status_var.get() or self.status_var.get() in [STRINGS[c].get("status_ready") for c in LANGS]:
            self.status_var.set(self.t("status_ready"))

        self.results_header_lbl.config(text=self.t("results_header"))
        self.save_result_btn.config(text=self.t("save_results_btn"))
        self.clear_results_btn.config(text=self.t("clear_results_btn"))

    # ---------------- Dastlabki bo'limlar ----------------
    def _load_default_categories(self):
        for name in DEFAULT_CATEGORY_NAMES["uz"]:
            self.categories[name] = []
        self._refresh_category_list()

    # ---------------- Bo'lim boshqaruvi ----------------
    def _refresh_category_list(self):
        self.cat_listbox.delete(0, tk.END)
        for name in self.categories:
            self.cat_listbox.insert(tk.END, f"{name}  ({len(self.categories[name])})")

    def _add_category(self):
        name = self._ask_string(self.t("dlg_new_category_title"), self.t("dlg_new_category_prompt"))
        if not name:
            return
        name = name.strip()
        if not name:
            return
        if name in self.categories:
            self._warning(self.t("dlg_warning_title"), self.t("dlg_duplicate_category"))
            return
        self.categories[name] = []
        self._refresh_category_list()

    def _delete_category(self):
        sel = self.cat_listbox.curselection()
        if not sel:
            return
        name = list(self.categories.keys())[sel[0]]
        if self._yesno(self.t("dlg_confirm_title"), self.t("dlg_confirm_delete_category_fmt", name=name)):
            del self.categories[name]
            self._refresh_category_list()
            self.val_listbox.delete(0, tk.END)
            self.values_label.config(text=self.t("no_category_selected"))

    def _current_category(self):
        sel = self.cat_listbox.curselection()
        if not sel:
            return None
        return list(self.categories.keys())[sel[0]]

    def _on_select_category(self, event=None):
        name = self._current_category()
        if name is None:
            return
        self.values_label.config(text=self.t("values_label_fmt", name=name, count=len(self.categories[name])))
        self.val_listbox.delete(0, tk.END)
        for v in self.categories[name]:
            self.val_listbox.insert(tk.END, v)

    # ---------------- Qiymat boshqaruvi ----------------
    def _add_value(self):
        name = self._current_category()
        if name is None:
            self._info(self.t("dlg_select_category_title"), self.t("dlg_select_category_msg"))
            return
        val = self.val_entry.get().strip()
        if not val:
            return
        if len(self.categories[name]) >= 100:
            self._warning(self.t("dlg_limit_title"), self.t("dlg_limit_msg"))
            return
        self.categories[name].append(val)
        self.val_entry.delete(0, tk.END)
        self._on_select_category()
        self._refresh_category_list()
        idx = list(self.categories.keys()).index(name)
        self.cat_listbox.selection_set(idx)

    def _delete_value(self):
        name = self._current_category()
        if name is None:
            return
        sel = self.val_listbox.curselection()
        if not sel:
            return
        del self.categories[name][sel[0]]
        self._on_select_category()
        self._refresh_category_list()
        idx = list(self.categories.keys()).index(name)
        self.cat_listbox.selection_set(idx)

    # ---------------- Profil saqlash/yuklash ----------------
    def _save_profile(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[(self.t("json_filetype"), "*.json")],
            initialfile="wordlist_profile.json",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.categories, f, ensure_ascii=False, indent=2)
        self._info(self.t("dlg_saved_title"), self.t("dlg_profile_saved_fmt", path=path))

    def _load_profile(self):
        path = filedialog.askopenfilename(filetypes=[(self.t("json_filetype"), "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("invalid format")
            self.categories = {k: list(v)[:100] for k, v in data.items()}
            self._refresh_category_list()
            self.val_listbox.delete(0, tk.END)
            self.values_label.config(text=self.t("no_category_selected"))
            self._info(self.t("dlg_loaded_title"), self.t("dlg_profile_loaded_msg"))
        except Exception as e:
            self._error(self.t("dlg_error_title"), self.t("dlg_profile_load_error_fmt", err=e))

    # ---------------- Generatsiya ----------------
    def _start_generation(self):
        min_len = self.min_len_var.get()
        max_len = self.max_len_var.get()
        if min_len > max_len:
            self._error(self.t("dlg_error_title"), self.t("dlg_length_error_msg"))
            return
        if not any(any(v.strip() for v in vals) for vals in self.categories.values()):
            self._warning(self.t("dlg_no_data_title"), self.t("dlg_no_data_msg"))
            return

        options = {
            "case": self.opt_case.get(),
            "leet": self.opt_leet.get(),
            "numbers": self.opt_numbers.get(),
            "special": self.opt_special.get(),
            "years": self.opt_years.get(),
            "pairs": self.opt_pairs.get(),
        }
        max_results = self.max_results_var.get()

        self.cancel_event.clear()
        self.generate_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.save_result_btn.config(state=tk.DISABLED)
        self.clear_results_btn.config(state=tk.DISABLED)
        self.result_listbox.delete(0, tk.END)
        self._last_results = []
        self.progress.start(10)
        self.status_var.set(self.t("status_generating"))

        def worker():
            try:
                results = build_wordlist(
                    {k: list(v) for k, v in self.categories.items()},
                    min_len, max_len, options, max_results,
                    self.progress_q, self.cancel_event,
                )
                self.progress_q.put(("done", results))
            except GenerationCancelled:
                self.progress_q.put(("cancelled", None))
            except Exception as e:
                self.progress_q.put(("error", str(e)))

        self.gen_thread = threading.Thread(target=worker, daemon=True)
        self.gen_thread.start()
        self.after(100, self._poll_queue)

    def _cancel_generation(self):
        self.cancel_event.set()
        self.status_var.set(self.t("status_cancelling"))

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self.progress_q.get_nowait()
                if kind == "progress":
                    # payload is already a human string from build_wordlist (uz-coded);
                    # we only localize the two generic cases we emit ourselves.
                    self.status_var.set(payload)
                elif kind == "done":
                    self._on_generation_done(payload)
                    return
                elif kind == "cancelled":
                    self._on_generation_stopped(self.t("status_cancelled"))
                    return
                elif kind == "error":
                    self._on_generation_stopped(self.t("status_error_fmt", err=payload))
                    return
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)

    def _on_generation_done(self, results):
        self._last_results = sorted(results)
        self.progress.stop()
        self.generate_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        has_results = bool(results)
        self.save_result_btn.config(state=tk.NORMAL if has_results else tk.DISABLED)
        self.clear_results_btn.config(state=tk.NORMAL if has_results else tk.DISABLED)
        self.status_var.set(self.t("status_done_fmt", n=len(results)))
        self.result_listbox.delete(0, tk.END)
        for w in self._last_results[:500]:
            self.result_listbox.insert(tk.END, w)
        if not results:
            self._info(self.t("dlg_no_results_title"), self.t("dlg_no_results_msg"))

    def _on_generation_stopped(self, msg):
        self.progress.stop()
        self.generate_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.status_var.set(msg)

    def _save_results(self):
        if not self._last_results:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[(self.t("txt_filetype"), "*.txt")],
            initialfile="wordlist.txt",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            for w in self._last_results:
                f.write(w + "\n")
        self._info(self.t("dlg_saved_title"), self.t("dlg_results_saved_fmt", n=len(self._last_results), path=path))

    def _clear_results(self):
        self._last_results = []
        self.result_listbox.delete(0, tk.END)
        self.save_result_btn.config(state=tk.DISABLED)
        self.clear_results_btn.config(state=tk.DISABLED)
        self.status_var.set(self.t("status_ready"))

    # ---------------- Virtual klaviatura ----------------
    def _set_active_entry(self, widget):
        self.active_entry = widget

    def _toggle_keyboard(self):
        if self.keyboard_window is not None and self.keyboard_window.winfo_exists():
            self._close_keyboard()
            return
        self._open_keyboard()

    def _open_keyboard(self):
        if self.active_entry is None:
            self.active_entry = self.val_entry

        win = tk.Toplevel(self)
        win.title(self.t("keyboard_title"))
        win.resizable(False, False)
        win.protocol("WM_DELETE_WINDOW", self._close_keyboard)
        self.keyboard_window = win
        self.vk_letter_buttons = []

        notebook = ttk.Notebook(win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        lang_order = ["uz", "tj", "ru", "en"]
        for lang_code in lang_order:
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=self.t("keyboard_tab_letters_fmt", lang=LANG_NAMES[lang_code]))
            for r, row in enumerate(KEYBOARD_LETTER_ROWS[lang_code]):
                row_frame = ttk.Frame(tab)
                row_frame.pack(pady=2)
                for ch in row:
                    btn = tk.Button(row_frame, text=ch, width=4, font=("Consolas", 11),
                                     command=lambda c=ch: self._vk_insert(c))
                    btn.pack(side=tk.LEFT, padx=1)
                    self.vk_letter_buttons.append((btn, ch))

        # Raqamlar qatori (barcha tillar uchun umumiy)
        num_label = ttk.Label(win, text=self.t("keyboard_numbers_label"), font=("Segoe UI", 9, "bold"))
        num_label.pack(anchor="w", padx=8, pady=(6, 0))
        num_frame = ttk.Frame(win)
        num_frame.pack(pady=2)
        for ch in KEYBOARD_NUMBER_ROW:
            tk.Button(num_frame, text=ch, width=4, font=("Consolas", 11),
                      command=lambda c=ch: self._vk_insert(c)).pack(side=tk.LEFT, padx=1)

        # Parol uchun maxsus belgilar (barcha tillar uchun umumiy)
        sp_label = ttk.Label(win, text=self.t("keyboard_special_label"), font=("Segoe UI", 9, "bold"))
        sp_label.pack(anchor="w", padx=8, pady=(6, 0))
        sp_outer = ttk.Frame(win)
        sp_outer.pack(pady=2, padx=6)
        per_row = 12
        for i in range(0, len(KEYBOARD_SPECIAL_CHARS), per_row):
            sp_frame = ttk.Frame(sp_outer)
            sp_frame.pack()
            for ch in KEYBOARD_SPECIAL_CHARS[i:i + per_row]:
                tk.Button(sp_frame, text=ch, width=4, font=("Consolas", 11),
                          command=lambda c=ch: self._vk_insert(c)).pack(side=tk.LEFT, padx=1, pady=1)

        # Boshqaruv tugmalari: Shift, Bo'sh joy, O'chirish, Tozalash, Yopish
        ctrl_frame = ttk.Frame(win)
        ctrl_frame.pack(fill=tk.X, padx=6, pady=(8, 6))
        self.vk_shift_btn = ttk.Button(ctrl_frame, text=self.t("keyboard_shift"), command=self._vk_toggle_shift)
        self.vk_shift_btn.pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text=self.t("keyboard_space"), command=lambda: self._vk_insert(" ")).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text=self.t("keyboard_backspace"), command=self._vk_backspace).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text=self.t("keyboard_clear"), command=self._vk_clear_field).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text=self.t("keyboard_close"), command=self._close_keyboard).pack(side=tk.RIGHT, padx=2)

        self._vk_refresh_case()

    def _close_keyboard(self):
        if self.keyboard_window is not None:
            self.keyboard_window.destroy()
            self.keyboard_window = None
            self.vk_letter_buttons = []

    def _vk_toggle_shift(self):
        self.vk_shift = not self.vk_shift
        self._vk_refresh_case()

    def _vk_refresh_case(self):
        for btn, lower_ch in self.vk_letter_buttons:
            btn.config(text=lower_ch.upper() if self.vk_shift else lower_ch)

    def _vk_insert(self, ch):
        if self.active_entry is None:
            return
        display_ch = ch.upper() if (self.vk_shift and ch.isalpha()) else ch
        try:
            self.active_entry.insert(tk.INSERT, display_ch)
            self.active_entry.focus_set()
        except tk.TclError:
            pass

    def _vk_backspace(self):
        if self.active_entry is None:
            return
        try:
            idx = self.active_entry.index(tk.INSERT)
            if idx > 0:
                self.active_entry.delete(idx - 1, idx)
            self.active_entry.focus_set()
        except tk.TclError:
            pass

    def _vk_clear_field(self):
        if self.active_entry is None:
            return
        try:
            self.active_entry.delete(0, tk.END)
            self.active_entry.focus_set()
        except tk.TclError:
            pass

