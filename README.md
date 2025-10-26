# SQL Query Builder CLI

CLI application featuring a type-safe SQL query builder inspired by jOOQ. This tool provides an elegant and fluent interface for building and executing SQL queries with SQLite.

## Features

- 🔒 **Type-safe query building** - Fluent API similar to jOOQ
- 📊 **SQLite database** - Lightweight and embedded
- 🎨 **Beautiful CLI interface** - Built with Click framework
- 📋 **Table formatting** - Clean output with tabulate
- ✅ **CRUD operations** - Complete Create, Read, Update, Delete support
- 🔍 **Query filtering** - Advanced search capabilities
- 🛡️ **Error handling** - Graceful error management

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the project**

```bash
# Create a project directory
mkdir sql-query-builder
cd sql-query-builder
```

2. **Install required dependencies**

```bash
pip install click tabulate
```

3. **Save the application**

Save the main code as `sql_cli.py`

4. **Make it executable (Optional - Linux/Mac)**

```bash
chmod +x sql_cli.py
```

## Usage

### Basic Command Structure

```bash
python sql_cli.py [COMMAND] [OPTIONS]
```

### Available Commands

#### User Management

**1. Add a new user**
```bash
python sql_cli.py add-user
# Or with options:
python sql_cli.py add-user --name "John Doe" --email "john@example.com" --age 30
```

**2. List all users**
```bash
python sql_cli.py list-users
```

**3. Get a specific user**
```bash
python sql_cli.py get-user 1
```

**4. Update user information**
```bash
python sql_cli.py update-user 1 --name "Jane Doe" --age 31
```

**5. Delete a user**
```bash
python sql_cli.py delete-user 1
```

**6. Search users with filters**
```bash
# Search users aged 25 or older
python sql_cli.py search-users --min-age 25
```

#### Product Management

**1. Add a new product**
```bash
python sql_cli.py add-product
# Or with options:
python sql_cli.py add-product --name "Laptop" --price 999.99 --stock 50
```

**2. List all products**
```bash
python sql_cli.py list-products
```

### Getting Help

```bash
# General help
python sql_cli.py --help

# Command-specific help
python sql_cli.py add-user --help
```

## Code Examples

### Query Builder API

The application uses a fluent query builder API similar to jOOQ:

#### SELECT Query
```python
# Simple select
users = qb.select('users').fetch()

# Select specific fields
users = qb.select('users').fields('id', 'name', 'email').fetch()

# With WHERE clause
users = qb.select('users').where('age >= ?', 25).fetch()

# With ORDER BY
users = qb.select('users').order_by('name', 'age DESC').fetch()

# With LIMIT
users = qb.select('users').limit(10).fetch()

# Fetch one record
user = qb.select('users').where('id = ?', 1).fetch_one()
```

#### INSERT Query
```python
# Insert with values
user_id = qb.insert('users').values(
    name='John Doe',
    email='john@example.com',
    age=30
).execute()

# Insert with set method
user_id = qb.insert('users')\
    .set('name', 'Jane Doe')\
    .set('email', 'jane@example.com')\
    .set('age', 28)\
    .execute()
```

#### UPDATE Query
```python
# Update with WHERE clause
rows = qb.update('users')\
    .set('name', 'Updated Name')\
    .set('age', 31)\
    .where('id = ?', 1)\
    .execute()
```

#### DELETE Query
```python
# Delete with WHERE clause
rows = qb.delete('users')\
    .where('id = ?', 1)\
    .execute()
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    age INTEGER
)
```

### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER DEFAULT 0
)
```

## Architecture

### Core Components

1. **QueryBuilder** - Main entry point for building queries
2. **SelectQuery** - Handles SELECT operations with filtering and ordering
3. **InsertQuery** - Manages INSERT operations
4. **UpdateQuery** - Handles UPDATE operations with WHERE clauses
5. **DeleteQuery** - Manages DELETE operations

### Design Patterns

- **Fluent Interface** - Method chaining for readable query building
- **Builder Pattern** - Step-by-step query construction
- **Command Pattern** - CLI commands for different operations

## Example Session

```bash
# Add some users
$ python sql_cli.py add-user --name "Alice Smith" --email "alice@example.com" --age 28
✓ User created successfully with ID: 1

$ python sql_cli.py add-user --name "Bob Johnson" --email "bob@example.com" --age 35
✓ User created successfully with ID: 2

# List all users
$ python sql_cli.py list-users
+------+--------------+-------------------+-------+
|   ID | Name         | Email             |   Age |
+======+==============+===================+=======+
|    1 | Alice Smith  | alice@example.com |    28 |
+------+--------------+-------------------+-------+
|    2 | Bob Johnson  | bob@example.com   |    35 |
+------+--------------+-------------------+-------+

# Search users
$ python sql_cli.py search-users --min-age 30
Users with age >= 30:
+------+--------------+-----------------+-------+
|   ID | Name         | Email           |   Age |
+======+==============+=================+=======+
|    2 | Bob Johnson  | bob@example.com |    35 |
+------+--------------+-----------------+-------+

# Update user
$ python sql_cli.py update-user 1 --age 29
✓ User 1 updated successfully!

# Add products
$ python sql_cli.py add-product --name "Laptop" --price 1299.99 --stock 15
✓ Product created successfully with ID: 1

$ python sql_cli.py list-products
+------+--------+---------+-------+
|   ID | Name   |   Price | Stock |
+======+========+=========+=======+
|    1 | Laptop | 1299.99 |    15 |
+------+--------+---------+-------+
```

## Extending the Application

### Adding New Tables

1. Add a table creation in `init_database()`:
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
""")
```

2. Create CLI commands for the new table following the existing patterns

### Adding Custom Queries

```python
@cli.command()
@click.pass_context
def custom_query(ctx):
    """Execute a custom query"""
    qb = ctx.obj['qb']
    
    # Your custom query logic here
    results = qb.select('users')\
        .fields('name', 'age')\
        .where('age > ?', 25)\
        .order_by('age DESC')\
        .limit(5)\
        .fetch()
```

## Error Handling

The application includes error handling for common scenarios:

- **Duplicate email entries** - Caught with `sqlite3.IntegrityError`
- **Missing records** - Returns appropriate messages
- **Invalid input** - Validated by Click decorators

## Dependencies

- **click** (v8.0+) - CLI framework
- **tabulate** (v0.9+) - Table formatting
- **sqlite3** - Built-in Python module

## Performance Considerations

- Uses parameterized queries to prevent SQL injection
- Connection pooling for better performance
- Efficient query building with minimal overhead
- Automatic transaction management

## Security

- **SQL Injection Protection** - All queries use parameterized statements
- **Input Validation** - Click handles type validation
- **Safe Delete Operations** - Confirmation prompts for destructive actions

## Limitations

- Currently supports SQLite only
- No support for JOIN operations (can be added)
- No support for complex aggregate functions (can be extended)
- Single database connection per session

## Future Enhancements

- [ ] Add support for PostgreSQL and MySQL
- [ ] Implement JOIN operations
- [ ] Add aggregate functions (COUNT, SUM, AVG)
- [ ] Support for transactions
- [ ] Migration system
- [ ] Query result caching
- [ ] Export data to CSV/JSON
- [ ] Import data from CSV/JSON

## Contributing

Feel free to extend this application with:
- New query builder features
- Additional CLI commands
- Support for other databases
- Better error handling
- Unit tests

## License

This project is provided as-is for educational purposes.

## Contact

For questions or suggestions, please refer to the documentation or extend the code as needed.

---

**Happy Querying! 🚀**
