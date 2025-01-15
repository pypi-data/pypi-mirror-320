# AllOnIADB

Connect to external database registered on the plateform.

```python
from alloniadb import connect

# Assuming you registered a DB connection named 'MyDB' on the plateform 
connection = connect("MyDB")
# The following synthax will depend on your actual DB type (SQL, Mongo...)
connection.request(...)
```