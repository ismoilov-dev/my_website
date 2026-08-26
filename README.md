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

## 🛡️ Production Deploy (Gunicorn + Systemd + Nginx)

1. **Systemd unit yaratish (`/etc/systemd/system/blog.service`):**
   ```ini
   [Unit]
   Description=Gunicorn daemon for Django Blog Application
   After=network.target

   [Service]
   User=ismat-dev
   Group=www-data
   WorkingDirectory=/home/ismat-dev/Desktop/Python/blog
   ExecStart=/home/ismat-dev/Desktop/Python/blog/venv/bin/gunicorn --config gunicorn.conf.py config.wsgi:application
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **Xizmatni yoqish va ishga tushirish:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable blog
   sudo systemctl start blog
   ```

3. **Nginx Reverse Proxy sozlamasi (`/etc/nginx/sites-available/blog`):**
   ```nginx
   server {
       listen 80;
       server_name ismatismoilov.uz www.ismatismoilov.uz;

       location /static/ {
           alias /home/ismat-dev/Desktop/Python/blog/staticfiles/;
       }

       location /media/ {
           alias /home/ismat-dev/Desktop/Python/blog/media/;
       }

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

---

## 🔄 CI/CD Avtomatlashtirish (GitHub Actions)

Loyiha `.github/workflows/` ichida 2 ta avtomatlashtirilgan ish jarayoniga ega:

1. **CI (`ci.yml`):** Har bir `push` va `PR` da linting (`ruff`), migratsiya konfliktlari tekshiruvi (`makemigrations --check`), production xavfsizlik tekshiruvi (`check --deploy`) hamda testlarni ishga tushiradi.
2. **CD (`deploy.yml`):** Testlar muvaffaqiyatli o'tgach va `main` branchiga push bo'lganda serverga SSH orqali ulanib, quyidagilarni avtomatik bajaradi:
   - `git pull`
   - `pip install -r requirements.txt`
   - `python manage.py migrate`
   - `python manage.py collectstatic --noinput`
   - `sudo systemctl restart blog`

### GitHub Secrets sozlamalari:
GitHub Repozitoriyangizning **Settings -> Secrets and variables -> Actions** bo'limida quyidagilarni kiriting:
- `SERVER_HOST`: Server IP yoki domeningiz
- `SERVER_USER`: Serverdagi SSH foydalanuvchi nomi
- `SERVER_SSH_KEY`: Serverga ulanish uchun SSH private key
- `SERVER_PROJECT_PATH`: Serverdagi loyiha papkasining yo'li (masalan: `/home/ismat-dev/Desktop/Python/blog`)

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
0 2 * * * /home/ismat-dev/Desktop/Python/blog/scripts/backup_db.sh >> /home/ismat-dev/Desktop/Python/blog/backups/backup.log 2>&1
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
