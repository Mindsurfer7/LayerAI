echo '#!/bin/bash
source venv/bin/activate
exec gunicorn layer_backend.wsgi:application --bind 0.0.0.0:8001' > start_django.sh
chmod +x start_django.sh