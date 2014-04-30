# Models

Rootio strives to provide the flexibility and power of a real radio station in a small package.
However, the database is rather detailed:

![DB Schema](/docs/dbschema.png?raw=true)

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
