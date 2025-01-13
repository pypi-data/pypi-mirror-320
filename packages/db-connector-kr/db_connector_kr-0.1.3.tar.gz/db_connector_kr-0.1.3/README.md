# db-connector-kr

`db-connector-kr` is a Python library designed to simplify database interactions across multiple DBMS platforms. It provides a consistent interface for executing queries, retrieving results as pandas DataFrames, and inserting data efficiently.

## Supported DBMS

The following DBMS platforms are considered:
- **PostgreSQL** (Supported)
- **Snowflake** (Supported)
- **MySQL** (Supported)
- **Microsoft SQL Server (MSSQL)** (Planned)
- **Oracle** (Planned)

Currently, only PostgreSQL, Snowflake, and MySQL are fully supported. MSSQL and Oracle support are planned for future updates.

---

## Installation

Install `db-connector-kr` via pip (once published to PyPI):
```bash
pip install db-connector-kr
```

### Optional Dependencies

**PostgreSQL**: To use PostgreSQL, install the additional dependency:
```bash
pip install db-connector-kr[postgres]
```

**!PostgreSQL**

---

## Features
1. Database Connection
- Automatically handles database connection initialization and validation.
2. Query Execution
- Retrieve results as pandas DataFrames (`read_to_df`).
- Execute DML queries such as INSERT, UPDATE, or DELETE (`execution_query`).
3. DataFrame Insertion
- Insert pandas DataFrames into database tables efficiently (`insert_df`)

---

## Usage

1. Initialization
```python
from db_connector import DBConnector

# Initialize the connector for PostgreSQL
config = {
    "dbms": "pg",
    "user": "your_username",
    "pw": "your_password",
    "dbname": "your_database",
    "host": "localhost",
    "port": 5432
}

connector = DBConnector(**config)
```

2. Retrieve Data as DataFrame
```python
query = "SELECT * FROM your_table;"
df = connector.read_to_df(query)
print(df.head())
```

3. Execute DML Queries
```python
query = "INSERT INTO your_table (id, name) VALUES (1, 'Alice');"
connector.execution_query(query)
```

4. Insert DataFrame into a Table
```python
import pandas as pd

# Example DataFrame
data = {"id": [1, 2], "name": ["Alice", "Bob"]}
df = pd.DataFrame(data)

# Insert into the table
connector.insert_df(df, table="your_table")
```

5. Close Connection
```python
connector.close()
```

---

## Planned Features
- Support for Microsoft SQL Server (MSSQL).
- Support for Oracle.
- Enhanced error handling and logging.

---

## Contributing
Contributions are welcome! If you would like to contribute, please:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with detailed information about your changes.

---

## License
This project is licensed under the MIT License.

---

## Contact 
For any inquiries or issues, please create an issue in the repository or contact the maintainer directly.