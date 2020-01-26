#!/usr/bin/env bash

source ../../venvs/rootio_web/bin/activate

cd .. && ./manage.py i18n_update_translations && ./manage.py i18n_compile_translations -f
