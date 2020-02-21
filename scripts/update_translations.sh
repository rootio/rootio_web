#!/usr/bin/env bash

#add something like this to crontab file -> crontab -e  in order to run this everyday
# 0 0 * * * cd /opt/rootio/rootio_web/scripts && bash update_translations.sh

source ../../venvs/rootio_web/bin/activate

cd .. && ./manage.py i18n_update_translations && ./manage.py i18n_compile_translations -f
