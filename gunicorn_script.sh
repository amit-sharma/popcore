#!/bin/bash
  set -e
  LOGFILE=/var/log/gunicorn/popcore.log
  LOGDIR=$(dirname $LOGFILE)
  NUM_WORKERS=3
  # user/group to run as
  USER=root
  GROUP=root
  cd /home/ubuntu/django_projects/popcore/trunk
  source /srv/python-environments/amitdjango/bin/activate
  test -d $LOGDIR || mkdir -p $LOGDIR
  exec gunicorn_django -w $NUM_WORKERS \
    --user=$USER --group=$GROUP --log-level=debug \
    --log-file=$LOGFILE 2>>$LOGFILE --timeout=30
