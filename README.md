# KPG — KHUD0X Password Generator

**KPG (KHUD0X Password Generator)** — Python dasturlash tilida ishlab chiqilgan, foydalanuvchi kiritgan ma’lumotlar asosida maxsus parollar ro‘yxatini (*wordlist*) yaratishga mo‘ljallangan lokal grafik dastur.

Loyiha parol xavfsizligini o‘rganish, dasturiy testlar, kiberxavfsizlik bo‘yicha ta’lim va ruxsat etilgan xavfsizlik sinovlari uchun ishlab chiqilgan.

KPG foydalanuvchiga turli kategoriyalardagi ma’lumotlarni birlashtirish, harf registrlarini o‘zgartirish, raqamlar va maxsus belgilar qo‘shish hamda hosil bo‘lgan kombinatsiyalarni wordlist shaklida yaratish imkonini beradi.

Dastur lokal foydalanish uchun mo‘ljallangan va odatiy ishlash jarayonida internetga ulanishni talab qilmaydi.

---

## ✨ Asosiy imkoniyatlar

- 🌐 **4 ta interfeys tili:** O‘zbekcha, Тоҷикӣ, Русский va English.
- 🗂️ **Kategoriyalar bo‘yicha ma’lumot kiritish:** ism, familiya, tug‘ilgan yil, shahar, hayvon va boshqa ma’lumotlar.
- 💾 **JSON profil tizimi:** kiritilgan ma’lumotlarni JSON formatida saqlash va keyinchalik qayta yuklash.
- 🔠 **Harf registrlarini o‘zgartirish:** katta va kichik harflardan foydalanib turli kombinatsiyalar yaratish.
- 🔢 **Raqamlar va yillar:** konfiguratsiyaga muvofiq raqamlar va yillarni qo‘shish.
- 🔣 **Maxsus belgilar:** tanlangan maxsus belgilarni kombinatsiyalarga qo‘shish.
- 🔄 **Leetspeak almashtirishlari:** ayrim harflarni o‘xshash raqamlar yoki belgilar bilan almashtirish.
- 🔗 **Kategoriyalarni birlashtirish:** turli ma’lumotlardan kombinatsiyalar hosil qilish.
- ⌨️ **Ko‘p tilli virtual klaviatura:** turli tillardagi belgilarni matn maydonlariga kiritishga yordam berish.
- 🖥️ **Grafik foydalanuvchi interfeysi (GUI):** asosiy funksiyalardan grafik muhit orqali foydalanish.
- 🧩 **Modulli arxitektura:** interfeys, generatsiya mantig‘i va tarjima matnlari alohida modullarga ajratilgan.
- 🔒 **Lokal ishlash:** dastur tashqi onlayn xizmatlarga bog‘liq bo‘lmagan holda ishlash uchun mo‘ljallangan.

---

## 🎯 Loyihaning maqsadi

KPG quyidagi vazifalar uchun yaratilgan:

- Parol xavfsizligi va foydalanuvchilar tanlaydigan parollar xususiyatlarini o‘rganish.
- Kiberxavfsizlik bo‘yicha amaliy mashg‘ulotlar o‘tkazish.
- O‘z tizimlarida yoki tegishli ruxsat berilgan muhitlarda xavfsizlik sinovlarini bajarish.
- Wordlist yaratish jarayonini o‘rganish va ma’lumotlar kombinatsiyalarini tahlil qilish.
- Parol xavfsizligi bo‘yicha laboratoriya ishlari va dasturiy testlarni tashkil etish.
- Python dasturlash tili va grafik interfeyslar bilan ishlash bo‘yicha amaliy tajriba orttirish.

---

## 🗂️ Loyiha tuzilishi

```text
KPG-khud0x-password-generation-/
├── core/
│   ├── __init__.py
│   └── wordlist_logic.py
├── gui/
│   ├── __init__.py
│   ├── app.py
│   └── keyboard_data.py
├── i18n/
│   ├── __init__.py
│   └── strings.py
├── main.py
├── README.md
└── LICENSE
```

### Modullar vazifasi

| Fayl yoki katalog | Vazifasi |
|---|---|
| `main.py` | Dasturni ishga tushirish nuqtasi |
| `core/wordlist_logic.py` | Wordlist yaratish va kombinatsiyalarni qayta ishlash mantig‘i |
| `gui/app.py` | `WordlistApp` klassi va grafik interfeys |
| `gui/keyboard_data.py` | Virtual klaviatura ma’lumotlari |
| `i18n/strings.py` | To‘rt tildagi interfeys matnlari |
| `LICENSE` | Loyiha litsenziyasi |
| `README.md` | Loyiha hujjatlari |

Modulli tuzilish kodni tushunish, texnik xizmat ko‘rsatish va kelajakda yangi funksiyalar qo‘shishni osonlashtirish uchun mo‘ljallangan.

---

## 🛠️ Texnologiyalar va talablar

- **Dasturlash tili:** Python 3.8 yoki undan yuqori.
- **Grafik interfeys:** Tkinter.
- **Ma’lumotlarni saqlash va almashish:** JSON.
- **Kombinatsiyalar bilan ishlash:** `itertools` va boshqa standart Python kutubxonalari.
- **Versiyalarni boshqarish:** Git.
- **Repository:** GitHub.

Agar loyiha faqat standart Python kutubxonalaridan foydalansa, tashqi Python paketlarini alohida o‘rnatish talab qilinmaydi.

**Eslatma:** Tkinter ayrim Linux distributivlarida alohida o‘rnatilishi mumkin. Aniq talablar loyihaning amaldagi kodiga bog‘liq.

---

## 🚀 O‘rnatish va ishga tushirish

### 🪟 Windows

**1. Python’ni o‘rnating.**

Python 3.8 yoki undan yuqori versiyasini rasmiy saytdan yuklab oling:

https://www.python.org/downloads/

O‘rnatish vaqtida **Add Python to PATH** parametrini belgilang.

**2. Repository’ni yuklab oling.**

Git o‘rnatilgan bo‘lsa, terminal yoki PowerShell’da quyidagilarni bajaring:

```bash
git clone https://github.com/khud0x/KPG-khud0x-password-generation-.git
cd KPG-khud0x-password-generation-
```

**3. Dasturni ishga tushiring.**

```bash
python main.py
```

Agar `python` buyrug‘i ishlamasa, quyidagini sinab ko‘ring:

```bash
py main.py
```

### 🐧 Linux — Kali Linux, Debian va Ubuntu

**1. Python versiyasini tekshiring.**

```bash
python3 --version
```

**2. Kerakli komponentlarni o‘rnating.**

Kali Linux, Debian va Ubuntu tizimlarida:

```bash
sudo apt update
sudo apt install python3 python3-tk git
```

**3. Repository’ni klonlang.**

```bash
git clone https://github.com/khud0x/KPG-khud0x-password-generation-.git
```

**4. Loyiha papkasiga o‘ting.**

```bash
cd KPG-khud0x-password-generation-
```

**5. Dasturni ishga tushiring.**

```bash
python3 main.py
```

Agar grafik interfeys ochilmasa, Tkinter o‘rnatilganini va tizimda grafik ish muhiti mavjudligini tekshiring. SSH orqali grafik muhitga ulanmagan serverda GUI oynasi ochilmasligi mumkin.

### 📦 ZIP orqali o‘rnatish

Git ishlatmasdan ham loyihani yuklab olish mumkin.

1. [KPG GitHub repository](https://github.com/khud0x/KPG-khud0x-password-generation-) sahifasini oching.
2. **Code → Download ZIP** tugmasini bosing.
3. ZIP arxivini oching.
4. Terminalni `main.py` joylashgan loyiha papkasida oching.
5. Operatsion tizimingizga mos buyruqni bajaring.

Windows:

```bash
python main.py
```

Linux:

```bash
python3 main.py
```

**Muhim:** `main.py`, `core/`, `gui/` va `i18n/` bir xil loyiha ildiz papkasida bo‘lishi kerak. Faqat alohida `main.py` faylini ko‘chirish yetarli emas, chunki dastur boshqa modullardan ham foydalanadi.

### 📱 Android

KPG Tkinter asosida ishlab chiqilganligi sababli Android’da odatiy APK kabi bevosita o‘rnatilmaydi.

Termux va mos grafik muhit yordamida ishga tushirish imkoniyatlari mavjud bo‘lishi mumkin, ammo buning uchun qo‘shimcha sozlashlar talab qilinadi va barcha qurilmalarda bir xil ishlashi kafolatlanmaydi.

Android uchun qulayroq versiya yaratish maqsadida dasturni mobil ilova yoki veb-texnologiyalar asosida qayta ishlab chiqish mumkin.

### 🍎 iOS

Tkinter dasturlari iPhone va iPad’da odatiy mobil ilova sifatida bevosita ishlamaydi. iOS uchun alohida mobil ilova yoki veb-versiya ishlab chiqish talab etiladi.

---

## 🔐 Maxfiylik va xavfsizlik

KPG lokal ishlash uchun mo‘ljallangan. Dasturga kiritilgan ma’lumotlar, JSON profillari va yaratilgan wordlist fayllari maxfiy ma’lumotlarni o‘z ichiga olishi mumkin.

Foydalanuvchilarga quyidagilar tavsiya etiladi:

- Shaxsiy ma’lumotlarni ehtiyotkorlik bilan kiriting.
- JSON profillari va yaratilgan fayllarni xavfsiz saqlang.
- Maxfiy ma’lumotlar, parollar yoki shaxsiy fayllarni ommaviy GitHub repository’lariga yuklamang.
- Dasturdan foydalanishdan oldin uning kodini ko‘rib chiqing.
- Sinovlarni faqat tegishli ruxsat mavjud bo‘lgan tizimlarda o‘tkazing.

Lokal ishlash xususiyati kodda tashqi tarmoq so‘rovlari yoki ma’lumot uzatish mexanizmlari mavjud emasligi tekshirilgandagina to‘liq tasdiqlanishi mumkin.

---

## ⚠️ Muhim eslatma va mas’uliyat

**KPG faqat ta’lim, dasturiy testlar va qonuniy, ruxsat etilgan kiberxavfsizlik sinovlari uchun mo‘ljallangan.**

Dasturdan foydalanishda quyidagi qoidalarga rioya qilish lozim:

- Dasturdan faqat qonuniy maqsadlarda foydalaning.
- Boshqa shaxslarning hisoblari, qurilmalari yoki tizimlariga tegishli ruxsatsiz kirishga urinmang.
- Xavfsizlik sinovlarini faqat o‘zingizga tegishli yoki tegishli ruxsat olingan tizimlarda bajaring.
- Boshqa shaxslarning maxfiyligini buzish yoki noqonuniy faoliyatni amalga oshirish uchun dasturdan foydalanmang.

### Asoschining pozitsiyasi

Loyiha asoschisi — **khud0x (KHUD0X)** — dasturdan noqonuniy maqsadlarda foydalanishni qo‘llab-quvvatlamaydi, rag‘batlantirmaydi yoki ma’qullamaydi. Loyiha ta’lim, test va qonuniy kiberxavfsizlik amaliyotlarini qo‘llab-quvvatlash maqsadida ishlab chiqilgan.

Foydalanuvchilar dasturdan foydalanish usullari va o‘z harakatlari uchun amaldagi qonunchilik hamda tegishli holatlarga muvofiq javobgar bo‘ladilar.

Ushbu eslatma asoschining pozitsiyasini bildiradi, lekin asoschini barcha holatlarda avtomatik ravishda huquqiy javobgarlikdan ozod qilmaydi. Har qanday huquqiy masala tegishli qonunchilik va muayyan vaziyatga qarab baholanadi.

---

## 📄 Litsenziya

Ushbu loyiha **MIT License** asosida tarqatiladi.

MIT litsenziyasi dasturiy ta’minotdan foydalanish, nusxalash, o‘zgartirish, birlashtirish, nashr etish, tarqatish, sublicenziyalash va sotishga ruxsat beradi. Bunda litsenziyada ko‘rsatilgan mualliflik huquqi va ruxsat bildirishnomalari kod nusxalarida yoki uning muhim qismlarida saqlanishi kerak.

Dastur hech qanday kafolatsiz, mavjud holicha taqdim etiladi. MIT litsenziyasining to‘liq shartlari repository ichidagi [`LICENSE`](LICENSE) faylida keltirilgan.

MIT litsenziyasidagi javobgarlikni cheklash bandi amaldagi qonunchilikda nazarda tutilgan barcha majburiyatlarni avtomatik ravishda bekor qiladi, degani emas.

---

## 👨‍💻 Muallif

**khud0x — Ubaydullo Xudoyberdiev**

- **GitHub:** [@khud0x](https://github.com/khud0x)
- **Portfolio:** [https://khud0x.uz](https://khud0x.uz)
- **Repository:** [KPG-khud0x-password-generation-](https://github.com/khud0x/KPG-khud0x-password-generation-)

---

## 📌 Loyiha haqida

KPG — kiberxavfsizlik, parol xavfsizligi va Python dasturlash yo‘nalishlarida amaliy tajriba orttirish uchun yaratilgan mustaqil loyiha.

Loyihaning asosiy maqsadi — parol xavfsizligini o‘rganish, test jarayonlarini qo‘llab-quvvatlash va kiberxavfsizlik bo‘yicha bilimlarni rivojlantirish.

**KPG — ta’lim, test va mas’uliyatli kiberxavfsizlik amaliyoti uchun.**
