# Django Portfolio & Blog Project

Ushbu loyiha Django 5, Gunicorn, Whitenoise va Nginx texnologiyalari asosida qurilgan Shaxsiy Portfolio hamda Blog veb-ilovasidir. Production muhitida systemd xizmati va GitHub Actions CI/CD orqali avtomatlashtirilgan holda ishlaydi.

---

## 📌 Texnologiyalar Steki

- **Framework:** Django 5.x
- **WSGI Server:** Gunicorn
- **Static fayllar:** WhiteNoise & Nginx
- **Ma'lumotlar bazasi:** SQLite (Standart) / PostgreSQL (Tayyor moslashtirilgan)
- **CI/CD:** GitHub Actions (Automated Testing & SSH Deployment)
- **Log va Monitoring:** Structured logging & `/healthz/` monitoring endpoint

---

## ⚙️ Muhit O'zgaruvchilari (`.env`)

Loyiha barcha maxfiy va muhitga bog'liq sozlamalarni `.env` faylidan o'qiydi. Namuna sifatida `.env.example` berilgan.

| O'zgaruvchi | Tavsif | Namuna qiymat |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Ishga tushirish muhiti (`local` yoki `production`) | `production` |
| `DEBUG` | Tuzatish rejimi (`True` yoki `False`) | `False` |
| `SECRET_KEY` | Django mahfiy kaliti | *Alohida maxfiy kalit* |
| `ALLOWED_HOSTS` | Ruxsat berilgan domen va IP'lar | `localhost,127.0.0.1,ismatismoilov.uz` |
| `CSRF_TRUSTED_ORIGINS` | CSRF ruxsat berilgan manbalar | `https://ismatismoilov.uz` |
| `DATABASE_URL` | *(Ixtiyoriy)* PostgreSQL ulanish manzili | `postgres://user:pass@localhost:5432/dbname` |
| `TIME_ZONE` | Vaqt zonasi | `Asia/Tashkent` |

---

## 🚀 Lokal Ishga Tushirish (Development)

1. **Repozitoriyani klonlash:**
   ```bash
   git clone https://github.com/ismoilov-dev/my_website.git
   cd my_website
   ```

2. **Virtual muhit yaratish va faollashtirish:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Kutubxonalarni o'rnatish:**
   ```bash
   pip install -r requirements.txt
   ```

4. **`.env` faylini sozlash:**
   ```bash
   cp .env.example .env
   ```
   *.env faylini ochib keragingizcha tahrirlang.*

5. **Migratsiyalarni bajarish va loyihani yuritish:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
   Ilova `http://127.0.0.1:8000` manzilida ishlaydi.

---

## 🛡️ Production Deploy (VPS: Gunicorn + systemd + Nginx)

Tayyor konfiguratsiya fayllari `deploy/` papkasida:

| Fayl | Vazifasi |
| :--- | :--- |
| `deploy/blog.service` | Gunicorn uchun systemd unit |
| `deploy/nginx.conf` | Nginx reverse proxy + static/media |
| `build.sh` | Serverdagi release skripti (migrate, collectstatic, restart, healthcheck) |

Quyidagi qadamlar `/srv/blog` yo'li va `ismat` foydalanuvchisi uchun yozilgan.
Boshqa yo'l ishlatsangiz, `deploy/` ichidagi fayllardagi yo'llarni ham
almashtiring.

### 1. Server tayyorlash
```bash
sudo apt update && sudo apt install -y python3-venv nginx git curl
sudo mkdir -p /srv/blog && sudo chown ismat:www-data /srv/blog

git clone https://github.com/ismoilov-dev/my_website.git /srv/blog
cd /srv/blog
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### 2. `.env` faylini yaratish
```bash
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
`.env` da albatta quyidagilarni to'ldiring:
```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<yuqoridagi buyruq bergan kalit>
ALLOWED_HOSTS=ismatismoilov.uz,www.ismatismoilov.uz
CSRF_TRUSTED_ORIGINS=https://ismatismoilov.uz,https://www.ismatismoilov.uz

# HTTPS hali sozlanmagani uchun DASTLAB False bo'lsin (pastga qarang)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```
> `SECRET_KEY` qo'yilmasa yoki `django-insecure-` bilan boshlansa, production
> rejimida ilova ataylab ishga tushmaydi.

### 3. systemd xizmati
```bash
sudo cp deploy/blog.service /etc/systemd/system/blog.service
sudo systemctl daemon-reload
sudo systemctl enable --now blog
sudo systemctl status blog
```

CD workflow servisni parolsiz qayta ishga tushira olishi uchun:
```bash
echo "ismat ALL=(ALL) NOPASSWD: /bin/systemctl restart blog, /bin/journalctl -u blog *" \
  | sudo tee /etc/sudoers.d/blog
sudo chmod 440 /etc/sudoers.d/blog
```

### 4. Nginx
```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/blog
sudo ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/blog
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

### 5. Birinchi release
```bash
cd /srv/blog && ./build.sh
```

### 6. HTTPS (Let's Encrypt)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d ismatismoilov.uz -d www.ismatismoilov.uz
```
Sertifikat o'rnatilgandan **keyin** `.env` da HTTPS bayroqlarini yoqing va
xizmatni qayta ishga tushiring:
```bash
sed -i 's/^SECURE_SSL_REDIRECT=False/SECURE_SSL_REDIRECT=True/;
        s/^SESSION_COOKIE_SECURE=False/SESSION_COOKIE_SECURE=True/;
        s/^CSRF_COOKIE_SECURE=False/CSRF_COOKIE_SECURE=True/' .env
sudo systemctl restart blog
```
> Bu bayroqlarni HTTPS'dan oldin yoqsangiz, brauzer cheksiz redirect'ga tushadi.

---

## 🔄 CI/CD Avtomatlashtirish (GitHub Actions)

Loyiha `.github/workflows/` ichida 2 ta avtomatlashtirilgan ish jarayoniga ega:

1. **CI (`ci.yml`):** Har bir `push` va `PR` da linting (`ruff`), migratsiya konfliktlari tekshiruvi (`makemigrations --check`), production xavfsizlik tekshiruvi (`check --deploy`) hamda testlarni ishga tushiradi.
2. **CD (`deploy.yml`):** **Faqat CI muvaffaqiyatli tugagandan keyin** ishga
   tushadi (`workflow_run`), ya'ni testdan o'tmagan kod serverga chiqmaydi.
   Serverga SSH orqali ulanib quyidagini bajaradi:
   - `git fetch` + `git reset --hard origin/main` (server nusxasi git bilan
     aynan bir xil bo'lishi uchun; `.env`, `db.sqlite3` va `media/` git'da
     kuzatilmagani uchun ularga tegmaydi)
   - `./build.sh` — dependency, `migrate`, `collectstatic`, `check --deploy`,
     `systemctl restart blog` va oxirida `/healthz/` orqali tekshiruv.
     Healthcheck o'tmasa, workflow xato beradi va `journalctl` loglarini
     ko'rsatadi.

`concurrency` sozlamasi tufayli bir vaqtda ikkita deploy ishlamaydi.
Actions bo'limidan qo'lda ham qayta deploy qilish mumkin (`workflow_dispatch`).

### GitHub Secrets sozlamalari:
GitHub Repozitoriyangizning **Settings -> Secrets and variables -> Actions** bo'limida quyidagilarni kiriting:
- `SERVER_HOST`: Server IP yoki domeningiz
- `SERVER_USER`: Serverdagi SSH foydalanuvchi nomi (masalan `ismat`)
- `SERVER_SSH_KEY`: Serverga ulanish uchun SSH private key
- `SERVER_SSH_PASSPHRASE`: (ixtiyoriy) kalit paroli
- `SERVER_PROJECT_PATH`: Serverdagi loyiha papkasi (masalan: `/srv/blog`)

---

## 💾 Ma'lumotlar Bazasi Zaxirasi (Daily Automated Backup)

Bazani avtomatik zaxiralash uchun `scripts/backup_db.sh` skripti tayyorlangan. Skript har kuni bazani arxivlaydi hamda 30 kundan eski arxivlarni tozalaydi.

### Qo'lda ishga tushirish:
```bash
./scripts/backup_db.sh
```

### Avtomatik `cron` sozlasi:
Serverda har kuni tunda 02:00 da ishga tushirish uchun `crontab -e` buyrug'ini bering va quyidagi qatorni qo'shing:
```cron
0 2 * * * /srv/blog/scripts/backup_db.sh >> /srv/blog/backups/backup.log 2>&1
```

---

## 🐘 SQLite -> PostgreSQL ga O'tish Tayyorgarligi

Kelajakda ma'lumotlar hajmi ortib, PostgreSQL ga o'tmoqchi bo'lsangiz:
1. PostgreSQL ma'lumotlar bazasi va foydalanuvchisini yarating.
2. `.env` faylingizga `DATABASE_URL` ni kiriting:
   ```env
   DATABASE_URL=postgres://user:password@localhost:5432/dbname
   ```
3. Migratsiyalarni o'tkazing: `python manage.py migrate`.
Loyiha `dj-database-url` orqali qo'shimcha kod o'zgarishisiz avtomatik PostgreSQL ga o'tadi.
