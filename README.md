# otit_ilmo
Event registration forms for Oulun Tietoteekkarit ry

## run development server
```shell
python3 -m venv env
source env/bin/activate
pip install -r requirements
export FLASK_APP=app.py
flask run
```

## starting gunicorn
```shell
gunicorn --workers=1 --worker-connections=400 --bind=0.0.0.0:62733 wsgi:app --name=ilmot --timeout 20 --daemon
```
