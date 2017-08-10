RethinkDBChanges
================
Monitor a specified channel and send a signal whenever a change occurs.  This can be an insertion or update to a document in the table.

Properties
----------
- **connect_timeout**: Amount of time to wait to connect before dropping.
- **database_name**: Name of database on the server.
- **host**: Server host ip, defaults to env variable.
- **port**: Server host port, defaults to env variable.
- **retry_options**: Configurables for retrying to connect to database
- **table**: Name of the table to watch in the current database.

Inputs
------
- **defualt**: Any list of signals.

Outputs
-------
- **default**: A signal with any changes that are pushed to the table that this block is watching.

Commands
--------

Dependencies
------------
-  rethinkdb

Output Example
--------------
Any changes that are pushed to the table that this block is watching.
This can be an insertion or update to a document in the table.
sample signal:
```
{
  'new_val': {
      'id': 'f25e058d-8164-4f7d-9546-6b26944c9828',
      'test': 200,
      'job_number': 2,
      }
}
```

RethinkDBDelete
===============
Delete an entry in a Rethink Database table.

Properties
----------
- **connect_timeout**: Amount of time to wait to connect before dropping.
- **database_name**: Name of database on the server.
- **enrich**: If true, include the original incoming signal in the output signal.
- **filter**: Control which documents are matched and updated based on these strings.
- **host**: Server host ip, defaults to env variable.
- **port**: Server host port, defaults to env variable.
- **retry_options**: Configurables for retrying to connect to database.
- **table**: Name of the table to watch in the current database.

Inputs
------
- **default**: Any list of signals, the block expects an attribute to match the filters in the database

Outputs
-------
- **default**: The result of the delete request to the server.  See example below.

Commands
--------

RethinkDBFilter
===============
Query a Rethink Database table.

Properties
----------
- **connect_timeout**: Amount of time to wait to connect before dropping.
- **database_name**: Name of database on the server.
- **enrich**: If true, include the original incoming signal in the output signal.
- **filter**: Control which documents are matched and updated based on these strings.
- **host**: Server host ip, defaults to env variable.
- **port**: Server host port, defaults to env variable.
- **retry_options**: Configurables for retrying to connect to database.
- **table**: Name of the table to watch in the current database.

Inputs
------
- **default**: Any list of signals, the block expects an attribute to match the filters in the database

Outputs
-------
- **default**: The result of the filter request to the server.

Commands
--------

RethinkDBInsert
===============
Insert an entry into a Rethink Database table.

Properties
----------
- **conflict**: How the block should handle conflicting insert attempts
- **connect_timeout**: Amount of time to wait to connect before dropping.
- **database_name**: Name of database on the server.
- **enrich**: If true, include the original incoming signal in the output signal.
- **host**: Server host ip, defaults to env variable.
- **object**: Data to insert into the database.
- **port**: Server host port, defaults to env variable.
- **retry_options**: Configurables for retrying to connect to database.
- **table**: Name of the table to watch in the current database.

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: The result of the insert request to the server.  See example below.

Commands
--------

RethinkDBUpdate
===============
Update a Rethink Database table.

Properties
----------
- **connect_timeout**: Amount of time to wait to connect before dropping.
- **database_name**: Name of database on the server.
- **enrich**: If true, include the original incoming signal in the output signal.
- **filter**: Control which documents are matched and updated based on these strings.
- **host**: Server host ip, defaults to env variable.
- **object**: Data to replace what's previously in the database.
- **port**: Server host port, defaults to env variable.
- **retry_options**: Configurables for retrying to connect to database.
- **table**: Name of the table to watch in the current database.

Inputs
------
- **default**: Any list of signals, the block expects an attribute to match the filters in the database

Outputs
-------
- **default**: The result of the update request to the server.  See example below.

Commands
--------

Dependencies
------------
-  rethinkdb

Output Example
--------------
The result of the update request to the server.
sample signal:
```
{
  'errors': 0,
  'unchanged': 0,
  'inserted': 0,
  'skipped': 0,
  'deleted': 0,
  'replaced': 1
}
```

