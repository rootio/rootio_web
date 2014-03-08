# Migrate
Using [Alembic](http://alembic.readthedocs.org/en/latest/index.html)

* create new alembic migration
`python manage.py migration auto`
* check it in and apply
`python manage.py migrate up`

# Backup and Restore

* create db backup
` pg_dump -Fc postgres > dump.sql `

* pull down from server
` scp rootio@176.58.125.166:/var/lib/postgresql/dump.sql .`

* restore
` pg_restore -d rootio -c -O -x dump.sql`
