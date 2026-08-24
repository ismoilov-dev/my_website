set -o errexit

pip install -r req.txt
python manage.py migrate
python manage.py createsuperuser --noinput
python manage.py collectstatic --noinput