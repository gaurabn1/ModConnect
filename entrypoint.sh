#python3 manage.py migrate --no-input
python3 manage.py collectstatic --no-input

gunicorn  ModConnect.wsgi:application --config gunicorn.py 
