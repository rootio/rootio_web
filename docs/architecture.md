# Architecture

The Rootio application holds the database of record for the radio system.
Models are shared with the telephony server, which can be running on the same
physical system or separately. Currently a symlink between folders ensures that
models are kept in sync between applications, but git submodules would also work.

A separate Scheduler application is a message broker between the web interface 
and the telephony server. On commit signals from SQLAlchemy, 0MQ messages are
sent over an IPC socket to the scheduler, which either forwards them via TCP to
telephony, or delays them until a specified time. This decoupled communication
provides flexibility, at the expense of slightly higher intial setup.

The Rootio application should be run by Apache or other WSGI web server. The
Scheduler flask application must be run by the same user, so that IPC sockets
are readable by both parties.