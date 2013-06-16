sudo bash << EOF 
cd /home/ubuntu/django_projects/popcore/trunk
source /srv/python-environments/amitdjango/bin/activate
gunicorn_django
EOF
