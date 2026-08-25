# 🚀 Django Blog & Portfolio Deployment Qo'llanmasi (Nginx + Gunicorn)

Ushbu qo'llanma **Django blog / portfoliodagi** barcha fyllar, rasmlar, sertifikatlar (**Media & Static files**) serverda (Nginx + Gunicorn) **hech qanday xatosiz va tezkor** ishlashini ta'minlash uchun tayyorlandi.

---

## 🛠️ Tayyorlangan Fayllar

Loyhada serverga joylash uchun quyidagi fayllar yaratildi va tayyorlandi:

| Fayl | Vazifasi |
| :--- | :--- |
| `nginx/nginx_blog.conf` | Nginx server konfiguratsiyasi (`/media/` va `/static/` fayllarni to'g'ridan-to'g mezon bilan tarqatadi) |
| `gunicorn.conf.py` | Gunicorn WSGI server sozlamalari |
| `blog.service` | Systemd xizmat fayli (server o'chib-yoniganda avtomatik ishga tushadi) |
| `deploy.sh` | 1-bosqichli avtomatik deploy va permission berish skripti |
| `.env.example` | Serverdagi maxfiy o'zgaruvchilar andozasi |
| `config/urls.py` | Nginx va Django media fayllarini har qanday rejimda xatosiz ko'rsatish zaxira mexanizmi |

---

## 📋 Step-by-Step Serverga O'rnatish Ketma-ketligi

### 1-qadam: Serverga loyhani yuklash va venv yaratish
Serveringizda loyha papkasiga kirib, virtual muhitni yaratib oling:

```bash
cd /var/www/blog  # (yoki loyhangiz joylashgan katalogni kiriting)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2-qadam: Environment (`.env`) sozlash
`.env.example` faylidan nusxa olib, `.env` faylini yarating:

```bash
cp .env.example .env
```
`.env` faylini ochib, domain va maxfiy kalitlarni o'zgartiring:
```env
DEBUG=False
SECRET_KEY=sizing_maxfiy_juda_uzun_kalitingiz
ALLOWED_HOSTS=ismatismoilov.uz,www.ismatismoilov.uz,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://ismatismoilov.uz,https://www.ismatismoilov.uz,http://ismatismoilov.uz
```

---

### 3-qadam: Avtomatik deploy skriptini yurgizish
Skript avtomatik tarzda:
1. Bazani migratsiya qiladi (`migrate`).
2. Static fayllarni to'playdi (`collectstatic`).
3. **Media papkalarini** (`media/certificates`, `media/feed`) yaratadi.
4. **Media va static papkalariga Nginx uchun to'g'ri ruxsatlar (`chmod -R 775`)** beradi.

```bash
chmod +x deploy.sh
./deploy.sh
```

---

### 4-qadam: Gunicorn Systemd xizmatini sozlash
`blog.service` faylini systemd katalogiga nusxalang:

```bash
# blog.service ichidagi fayl yo'llarini (WorkingDirectory, ExecStart) serveringizdagi mos yo'l bilan tekshiring!
sudo cp blog.service /etc/systemd/system/blog.service

# Xizmatni yoqish va ishga tushirish:
sudo systemctl daemon-reload
sudo systemctl start blog
sudo systemctl enable blog
```

Xizmat holatini tekshirish:
```bash
sudo systemctl status blog
```

---

### 5-qadam: Nginx Serverni Sozlash (Media Fayllar Xatosiz Ishlashi Uchun)

1. `nginx/nginx_blog.conf` faylidagi **`alias`** yo'llari serveringizdagi loyha yo'li bilan mos kelishini tekshiring (`/var/www/blog/...` yoki `/home/.../blog/...`).
2. Nginx sayt konfiguratsiyasiga joylang:

```bash
sudo cp nginx/nginx_blog.conf /etc/nginx/sites-available/blog
sudo ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/
```

3. Nginx sintaksisini tekshirish va qayta yuklash:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

### 6-qadam: SSL Certbot (HTTPS) O'rnatish
Saytingizga tekin SSL sertifikat o'rnatish uchun:

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d ismatismoilov.uz -d www.ismatismoilov.uz
```

---

## 🔍 Media Fayllar Xatosiz Ishlashining 3 Oltin Qoidasi

1. **413 Request Entity Too Large (Katta fayl yuklanmasligi xatosi)**:
   - `nginx_blog.conf` fayliga `client_max_body_size 100M;` qo'shilgan. Bu katta PDF sertifikatlar va rasmlar yuklanishini ta'minlaydi.

2. **Nginx Media Permissions (Ruxsatlar xatosi)**:
   - Nginx `www-data` foydalanuvchisi media papkasini o'qiy olishi kerak.
   - `./deploy.sh` skripti avtomatik bajaradi (`chmod -R 775 media/`).

3. **Fallback Media Routing (`config/urls.py`)**:
   - `urls.py` fayliga `re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})` qo'shildi. Nginx o'tkazib yuborgan taqdirda ham Django media fayllarni 404 bermay xatosiz beradi!
