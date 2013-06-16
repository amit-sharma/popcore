#!/usr/local/bin/bash 
 
#Activate the virtualenv 
source /users/home/aagns9c3/django_projects/mysite/bin/activate
export DJANGO_SETTINGS_MODULE=popcore.settings
export LD_LIBRARY_PATH=/usr/local/lib/mysql:$LD_LIBRARY_PATH

 
PROJECT_NAME="popcore" 
PROJECT_DIR="/users/home/aagns9c3/django_projects/mysite/popcore" 
PID_FILE="/users/home/aagns9c3/django_projects/mysite/popcore/popcore.pid" 
SOCKET_FILE="/users/home/aagns9c3/django_projects/mysite/popcore/popcore.socket" 
BIN_PYTHON="/users/home/aagns9c3/django_projects/mysite/bin/python" 
DJANGO_ADMIN="/users/home/aagns9c3/django_projects/mysite/bin/django-admin.py" 
OPTIONS="maxchildren=2 maxspare=2 minspare=1" 
METHOD="prefork" 
 
case "$1" in
    start) 
      # Starts the Django process 
      echo "Starting Django project" 
      $BIN_PYTHON $DJANGO_ADMIN runfcgi $OPTIONS method=$METHOD socket=$SOCKET_FILE pidfile=$PID_FILE 
  ;;  
    stop) 
      # stops the daemon by cating the pidfile 
      echo "Stopping Django project" 
      kill `/bin/cat $PID_FILE` 
  ;;  
    restart) 
      ## Stop the service regardless of whether it was 
      ## running or not, start it again. 
      echo "Restarting process" 
      $0 stop
      $0 start
  ;;  
    *)  
      echo "Usage: init.sh (start|stop|restart)" 
      exit 1
  ;;  
esac 

