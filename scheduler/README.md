# ABOUT

This is the scheduler daemon that collects messages from rootio_web and sends them to rootio_telephony when needed. It should be run on the same server and under the same process as the rootio_web server (`www-data`), so that both applications can access the IPC socket.

## Start

`python run.py`