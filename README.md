# RethinkDB 

Blocks for communicating with and monitoring a RethinkDB server.


## RethinkDBChanges

Properties
--------------
-  table: name of the table to watch in the current database
-  host: server host ip, defaults to env variable
-  port: server host port, defaults to env variable
-  database_name: name of database on the server
-  connect_timeout: amount of time to wait to connect before dropping

Dependencies
----------------
-  rethinkdb

Commands
----------------
-  Get server info: Gets information about the current connected RethinkDB server
-  Reconnect to server: Reconnects to the last connected RethinkDB server
-  List server databases: List all databases on the current connected server
-  List database tables: List all tables in the current database

Input
-------
None

Output
---------
Any changes that are pushed to the table that this block is watching. 
This can be an insertion or update to a document in the table.

sample signal: 

```
{
  'new_val': {
      'id': 'f25e058d-8164-4f7d-9546-6b26944c9828',
      'test': 200,
      'job_number': 2, 
      },
  'old_val': {
      'id': 'f25e058d-8164-4f7d-9546-6b26944c9828', 
      'test': 100, 
      'job_number': 2, 
      }
}
```


## RethinkDBUpdate

Properties
--------------
-  table: name of the table to watch in the current database
-  host: server host ip, defaults to env variable
-  port: server host port, defaults to env variable
-  database_name: name of database on the server
-  connect_timeout: amount of time to wait to connect before dropping
-  filters: control which documents are matched and updated based on these strings

Dependencies
----------------
-  rethinkdb

Commands
----------------
-  Get server info: Gets information about the current connected RethinkDB server
-  Reconnect to server: Reconnects to the last connected RethinkDB server
-  List server databases: List all databases on the current connected server
-  List database tables: List all tables in the current database

Input
-------
Any list of signals. This block expects incoming signals to have attributes
that are matched with filters and will exist in the table. 

Output
---------
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
