# API

## General

CRUD routes are provided by [Flask-Restless](http://flask-restless.readthedocs.org/), which uses JSON syntax to provide [pagination](http://flask-restless.readthedocs.org/en/latest/requestformat.html#clientpagination) and [search](http://flask-restless.readthedocs.org/en/latest/searchformat.html#searchformat).

## Authentication

Each API call must be identified either with a 10-digit station api_key parameter, or basic HTTP authentication provided by Flask. The API key is preferred for station to server communication.

## Routes
### CRUD
* http://demo.rootio.org/api/login
* http://demo.rootio.org/api/logout
* http://demo.rootio.org/api/person
* http://demo.rootio.org/api/station
* http://demo.rootio.org/api/program
* http://demo.rootio.org/api/scheduledprogram
* http://demo.rootio.org/api/episode
* http://demo.rootio.org/api/recording
* http://demo.rootio.org/api/phonenumber
* http://demo.rootio.org/api/call
* http://demo.rootio.org/api/message

### Non-CRUD
__these do not respond to the ?updated_since parameter__
* http://demo.rootio.org/api/station/ID/current_program
* http://demo.rootio.org/api/station/ID/on_air
* http://demo.rootio.org/api/station/ID/next_program
* http://demo.rootio.org/api/station/ID/current_block
* http://demo.rootio.org/api/station/ID/phone_numbers

__these have specific datetime parameters__
* http://demo.rootio.org/api/station/ID/schedule?all
* http://demo.rootio.org/api/station/ID/schedule?start=2014-03-01&end=2014-04-01

__these do respond to the ?updated_since parameter__
* http://demo.rootio.org/api/station/ID/programs
* http://demo.rootio.org/api/program/ID/episodes

### Allow form-data POST
* http://demo.rootio.org/api/station/ID/analytic


## Search Parameters
Flask-Restless provides a powerful search format using [JSON syntax](http://flask-restless.readthedocs.org/en/latest/searchformat.html)

eg: `http://demo.rootio.org/api/scheduledprogram?q={"filters":[{"name":"id","op":"gt","val":25}]}`

## Updated Since
The ?updated_since parameter is provided as an alias to the search syntax for the common case. Passing a valid ISO datetime will limit the results to include only objects updated after that time.

eg: `http://demo.rootio.org/api/scheduledprogram?updated_since=2014-03-20T00:00:00Z-8:00`