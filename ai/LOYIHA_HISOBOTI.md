# VUCA AXLOQ — Gamifikatsiyalashgan Ta’lim Platformasi
## Loyiha Bo‘yicha Bajarilgan Ishlar Hisoboti

---

###  Loyiha Haqida Qisqacha
* **Loyiha nomi:** 9–11-sinf o‘quvchilarining VUCA sharoitida axloqiy dunyoqarashini rivojlantirish platformasi
* **Loyiha rahbari:** **Xasanova Bo‘rigul Hasan qizi**
* **Konseptsiya:** VUCA-dunyo (Volatility — O‘zgaruvchanlik, Uncertainty — Noaniqlik, Complexity — Murakkablik, Ambiguity — Ziddiyatlilik/Noaniqlik) sharoitida zamonaviy maktab o‘quvchilarining ma’naviy-axloqiy immunitetini mustahkamlash.
* **Dizayn va tajriba:** Duolingo 1:1 gamifikatsiyalashgan, interaktiv, audio-vizual va motivatsion ta’lim tizimi.
* **Asosiy til:** Toza o‘zbek lotin alifbosi (barcha chet va ruscha so‘zlar ta’limiy kontekstga moslashtirilgan).

---

## 1. DUOLINGO 1:1 ANIMATSIYALARI VA ILG‘OR LOTTIE TIZIMI

Duolingo rasmiy platformasidagi (`https://ru.duolingo.com/`) barcha mashhur animatsion sahnalar va SVG vektor qahramonlar loyihamizga 1:1 aniqlikda olib kelindi va moslashtirildi:

| № | Qism / Mavzu | Lottie Fayli | Sahna va Qahramon Harakati |
|---|---|---|---|
| 1 | **Mutlaqo bepul, qiziqarli va samarali ta’lim** | `effective_lottie.json` | Duo boyo‘g‘lisi qanot qoqib sakraydi, quvnoq tabassum qiladi va o‘quvchini darsga chorlaydi. |
| 2 | **Ilmiy-pedagogik yondashuv** | `science_lottie.json` | Duo oq laboratoriya xalati va ko‘zoynagida, tajriba kolbalaridagi kimyoviy suyuqliklar qaynaydi va pufakchalar otiladi. |
| 3 | **Ta’limga kuchli rag‘bat va motivatsiya** | `motivation_lottie.json` | Olovli kunlik seriya (streak) alanga oladi, qimmatbaho olmoslar va yutuq nishonlari porlaydi. |
| 4 | **Har bir o‘quvchiga individual yondashuv** | `personalized_lottie.json` | Adaptiv ta’lim kartalari, dars sur’ati va dinamik qahramon harakatlari. |
| 5 | **Istalgan vaqtda va istalgan joyda ta’lim** | `anytime_lottie.json` | Noutbuk, planshet, smartfon va shahar manzarasi uyg‘unlashgan keng panoramik harakatlanuvchi sahna. |
| 6 | **VUCA olamida o‘z kelajagingizni quring!** | `bottom_lottie.json` | Pastki CTA bannerida do‘stona jamoaviy bayramona animatsiya. |

### Texnik yechimlar:
* **Uzluksiz 30 FPS Sikl:** Bodymovin/Lottie kutubxonasi orqali barcha animatsiyalar cheksiz, to‘xtovsiz (`loop: true, autoplay: true`) va silliq ishga tushirildi.
* **SVG Vektor Transformatsiyalari:** SVG guruhlarining matritsali harakatlarini cheklab qo‘ygan barcha CSS to‘siqlari olib tashlandi.
* **CSS Bob & Float Tebranishi (`@keyframes duoFloatSway`):** Animatsiya kanvaslari sahifada doimiy ravishda yengil tebranib, Duolingoga xos jonli muhit yaratadi.
* **Scroll Dinamikasi:** Foydalanuvchi sahifani tepaga yoki pastga aylantirganda kartochkalar va SVG qahramonlar 3D parallaks bilan nozik burchak ostida buriladi (`transform: translate3d(...) rotate(...) scale(...)`). Faol scroll qilinganda Lottie ijro tezligi 1.35x gacha oshib, to‘xtaganda 1.0x ga silliq qaytadi.

---

## 2. INTERFEYS VA FOYDALANUVCHI TAJRIBASI (UI/UX)

### A. Tungi va Kunduzgi Rejim (Dark / Light Mode)
* Yuqori sarlavhada (desktop va mobile header) hamda mobil menyu ichida quyosh/oy tugmasi (`data-theme-toggle`).
* Bir marta bosish bilan butun sayt ranglar palitrasi (fon, matnlar, kartochkalar, bordurlar, shadowlar) to‘liq o‘zgaradi.
* Foydalanuvchi tanlagan rejim brauzerning `localStorage` xotirasida eslab qolinadi.
* Barcha tugmalar va ikonkalarning holati bir zumda o‘zaro sinxronlashadi.

### B. Mobil Gamburger Menyu va Moslashuvchanlik
* Kichik ekranli qurilmalarda (smartfon, planshet) sarlavhada ixcham `.mobile-actions` paneli paydo bo‘ladi:
  - Mavzuni almashtirish (Dark/Light)
  - Duolingo ovozlarini yoqish/o‘chirish
  - Gamburger menyu (`☰` -> `✕`)
* Menyu ichidagi har qanday havola bosilganda yoki menyudan tashqariga bosilganda oyna avtomatik va silliq yopiladi.
* Pastki navigatsiya paneli (`.bottom-nav`) orqali asosiy bo‘limlar (Bosh sahifa, Maqsad, O‘rganish yo‘li, Diplomlar) doimo qo‘l ostida bo‘ladi.

### C. Duolingo Web Audio Synthesizer (Tabiiy Brauzer Audio API)
* Hech qanday tashqi og‘ir audio fayllarsiz, toza Web Audio API osillyatorlari orqali Duolingo tovushlari yaratildi:
  - Tugmalar, kartochkalar va filtrlarni bosganda: **440–580 Hz taktil pop ovozi**.
  - Dars yoki test muvaffaqiyatli yakunlanganda: **C5, E5, G5, C6 notalaridagi 4 bosqichli tantanali major akkordi**.
  - Mukofot sandig‘i ochilganda: **5 notali fanfare sadosi**.
* Ovoz effektlarini istalgan payt yoqish/o‘chirish imkoniyati (`sound-toggle`).

### D. Taktil Tugma Bosilishi (Tactile Button Ripple)
* Barcha `.btn`, `.path-card`, `.vuca-tile` elementlari bosilganda to‘lqinsimon yengil vizual samara paydo bo‘ladi.
* `pointer-events: none !important;` xossasi orqali tugmalarning bosilishi hech qachon kechikmaydi, to‘silmaydi yoki qotmaydi.

---

## 3. MICROLEARNING VA RASMIY HUJJATLAR TIZIMI

### A. 20 ta Infografika Uchun Zamonaviy Slayder & Lightbox Modal
* **Karusel:** 20 ta mavzulashtirilgan infografika avtomatik (5 soniya) va qo‘lda aylanadi.
* **Boshqaruv elementlari:** Oldinga (`›`), orqaga (`‹`), miniatyuralar (thumbnails), vaqtincha to‘xtatish/davom ettirish (**Pauza / Play**) tugmalari.
* **Scroll Jump Tuzatildi:** Slayder aylanganda sahifaning tepaga sakrab ketish muammosi to‘liq yo‘qotildi.
* **To‘liq Ekran Lightbox Modali:** Har qanday infografikani to‘liq ekranda kattalashtirib, matnlari bilan birga o‘qish, klaviaturadagi `Escape`, `ArrowLeft`, `ArrowRight` orqali ko‘rish va rasmni bitta tugma bilan yuklab olish imkoniyati yaratildi.

### B. 20 ta Rasmiy Word (.docx) va PDF (.pdf) Hujjatlar Bo‘limi
* Platformaga kursning barcha me’yoriy hujjatlari joylandi:
  - 6 ta qulay toifadagi interaktiv filtr tugmalari:
    1. *Barchasi* (20 ta)
    2. *Word fayllar (.docx)* (10 ta)
    3. *PDF hujjatlar (.pdf)* (10 ta)
    4. *Kurs dasturlari*
    5. *Ish rejalari*
    6. *Huquqiy asoslar*
* Format bo‘yicha vizual ajratish:
  - `.DOCX` hujjatlar ko‘k hoshiya va Word belgisi bilan.
  - `.PDF` hujjatlar qizil hoshiya va PDF belgisi bilan.
* `DEBUG=False` rejimida ham barcha 40 ta media fayl (20 ta rasm, 20 ta hujjat) HTTP 200 OK bilan uzluksiz yuklanadi.

---

## 4. GAMIFIKATSIYA VA MOTIVATSIYA TIZIMI

* **Panda Maskot va Motivatsion Dialoqlar:**
  - 8 ta chuqur ma’noli axloqiy va VUCA dunyoqarash iqtiboslari navbat bilan chiqib turadi.
  - Panda bosilganda elastik deformatsiya ("squish & stretch"), dialoq pufagi tebranishi, pop ovozi va ekranda uchuvchi rag‘bat zarralari (`⚡ +10 XP`, `🔥 Zo‘r!`, `💎 +1 Olmos!`).
* **Mukofot Sandiqlari (Unit Chests):**
  - O‘quvchi yo‘lidagi har bir modul oxirida ochiladigan qimmatbaho sandiqlar (fanfare ovozi, konfetti va +25 XP mukofot).
* **Mahalliy Konfetti Tizimi:**
  - `canvas-confetti` kutubxonasi to‘liq mahalliy `static/js/confetti.min.js` fayliga olindi, tashqi CDN kutishlariga barham berildi.

---

## 5. XAVFSIZLIK, BARQARORLIK VA TEZLIK

1. **Orqa Fondagi Port Muammosi Hal Etildi:**
   - 8000-portni egallab, `app.js` faylini eski o‘lchamda uzib yuborayotgan eski Python jarayoni (PID: 12072) to‘xtatildi.
   - Yangi server ishga tushirilib, to‘liq 1007 qatorlik skript uzatilmoqda.
2. **Kesh Muammosi (Cache-Busting):**
   - Brauzerlar eski keshdagi fayllarni yuklab olmasligi uchun versiyalash o‘rnatildi (`app.js?v=3.5`).
3. **Izolyatsiyalangan Xatolik Himoyasi:**
   - [static/js/app.js](file:///D:/tyutors-site-for-yashin-aka/static/js/app.js) dagi barcha bo‘limlar alohida `try/catch` bloklariga o‘ralgan. Biror element yo‘qligi boshqa tugmalar faoliyatini to‘xtatib qo‘ymaydi.
4. **Statik Fayllar Sinxronizatsiyasi:**
   - `collectstatic --noinput` orqali Whitenoise siqilgan `.br` va `.gz` paketlari qayta yaratildi.
5. **Til Tozaligi:**
   - Saytda birorta ham ruscha so‘z qolmadi. Barcha ma’lumotlar 9–11-sinf o‘quvchilariga mos toza o‘zbek tilida taqdim etilgan.
   - Loyiha rahbari nomi: **Xasanova Bo‘rigul Hasan qizi**.

---
*Hisobot sanasi: 2026-yil 12-sentyabr*
