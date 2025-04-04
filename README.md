

python -m venv venv
source venv/bin/activate

 python manage.py runserver  

 
 <!-- 

 Flutter:
    - overflow hidden
    - scrollable 
    - err visibility in login
    

 Python:


  -->
  
  
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install djoser

python manage.py makemigrations users
python manage.py migrate

pm2 start ./start_django.sh --name django-layerai