# Models

RootIO strives to provide the flexibility and power of a real radio station in a small package.
However, the resulting database is rather detailed:

![DB Schema](/docs/dbschema.png?raw=true)

Don't fret, all the pieces fit together.

The central object is the Station, which has fields for the radio signal frequency, location, client update parameters, and an owner or primary manager.

Programs are a recurring show with a length and an update recurrence (eg: weekly, daily, hourly etc). Programs are defined by a ProgramType, which provides information on how the show progresses (eg: when listener calls come in, which intro or outro jingle to use, etc). This definition is shared with the telephony server, which handles incoming calls and text messages.

Once a show has aired it is stored as an Episode, which is provides a link between a Program and a Recording. Programs to air in the future do not have Episodes, but are ScheduledPrograms, which is a promise to air a Program on a Station between a start and end time.

A ScheduledBlock provides the structure of the broadcast day (eg: drive-time in the morning, talk shows midday, news in the evening, and music at night). PaddingContent is linked to a ScheduledBlock, so that advertisers or sponsors can be target a particular part of the day's audience.

Networks of Stations can share PaddingContents, Programs, and administrators. Stations, Programs and people have Languages, so that audiences can hear appropriate local content.

For the telephony server, Calls or Messages go through a Gateway, and are connected to a PhoneNumber. When a show is being broadcast on a Station, incoming calls and messages are stored in an OnAirProgram, which provides quick links between "live" objects and show metrics.

StationAnalytics are requested at a configurable interval, and store battery level, gsm signal (in dB), wifi connectivity, memory / cpu / storage utilization, the headphone plug connection, and GPS position. This allows the Station or Network manager to know the status of Stations in the field, and a dashboard provides insights on where their attention is needed most.

Users are accounts that have access to the website and API. Persons are not users of the system, but a rolodex of people who may be on air personalities, or reporters from the field. Their title, name, gender, contact information, role and privacy settings are stored for lookup by Users or to provide cues to a show host.

# Migrations
Changes to the schema are managed by [Alembic](http://alembic.readthedocs.org/en/latest/index.html)

* make changes
* create new alembic migration

`python manage.py migration "description of changes"`

* edit automatic operations as necessary

`vi alembic/versions/REVISION_ID_description.py`

* apply it to your local database

`python manage.py migrate up`

* check it in and deploy

`git commit -a alembic/versions/REVISION_ID_description.py`

`git push origin master`

`cd deploy; fab deploy`


# Backup and Restore

* create db backup

`ssh rootio@176.58.125.166; su postgres`

`pg_dump -Fc postgres > dump.sql`

* copy down from server

`scp rootio@176.58.125.166:/var/lib/postgresql/dump.sql .`

* restore

`pg_restore -d rootio -c -O -x dump.sql`
