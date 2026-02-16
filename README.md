# Magazin tizimi

Kichik do'kon uchun multi-user magazin tizimi. O'zbek tilida, brauzer orqali ishlaydi.

## Render.com da bepul joylashtirish

### 1. GitHub ga yuklash

```bash
git init
git add .
git commit -m "Magazin tizimi"
git branch -M main
# GitHub da yangi repo yarating, keyin:
git remote add origin https://github.com/YOUR_USERNAME/magazin-tizimi.git
git push -u origin main
```

### 2. Render.com da sozlash

1. [render.com](https://render.com) - ro'yxatdan o'ting (bepul)
2. **New +** → **Web Service**
3. GitHub reponi ulang
4. Sozlamalar:
   - **Name:** magazin-tizimi
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. PostgreSQL qo'shish

1. **New +** → **PostgreSQL**
2. **Name:** magazin-db
3. **Create Database**
4. Database yaratilgach, **Internal Database URL** ni nusxalang

### 4. Web Service ga ulash

1. Web Service → **Environment** → **Add Environment Variable**
2. **Key:** `DATABASE_URL`
3. **Value:** PostgreSQL Internal URL (nusxalangan)

4. **Save Changes** - avtomatik qayta deploy bo'ladi

### 5. Kirish

- URL: `https://magazin-tizimi.onrender.com` (yoki sizning nomingiz)
- **Admin:** admin / admin123 (birinchi kirishda yaratiladi)

---

## Eslatma

- **Python versiyasi:** 3.10 yoki 3.11 tavsiya etiladi (Render 3.11 ishlatadi)
- Python 3.14 yoki juda yangi versiyalar ba'zi kutubxonalar bilan muammo qilishi mumkin

## Lokal ishlatish (Windows)

### SQLite bilan (PostgreSQL o'rnatmasdan)

```bash
# Python 3.10 yoki 3.11 ishlatish tavsiya etiladi
python -m venv venv
venv\Scripts\activate

# O'rnatish (lokal - psycopg2 olinmaydi)
pip install -r requirements-local.txt

# Ishga tushirish
python main.py
```

Brauzerda: http://localhost:8000

### PostgreSQL bilan

1. PostgreSQL o'rnating
2. `.env` fayl yarating:
```
DATABASE_URL=postgresql://postgres:parol@localhost:5432/sklad_db
SECRET_KEY=o'zingizning-maxfiy-kalitingiz
```

3. `python main.py`

---

## Imkoniyatlar

- **Multi-user:** 2-4 foydalanuvchi bir vaqtda
- **Rollar:** Admin (barcha huquqlar), Kassir (sotuv)
- **Mahsulotlar:** qo'shish, tahrirlash, arxivlash (soft delete)
- **Sotuv:** mahsulot tanlash, savatcha, foyda hisoblash
- **Ombor:** jami mahsulot, sotilgan, qolgan, foyda
- **Hisobot:** bugungi foyda, eng ko'p sotilgan mahsulotlar
- **Responsive:** telefon va kompyuter
