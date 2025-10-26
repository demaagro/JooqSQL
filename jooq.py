"""
SQL Query Builder CLI - A type-safe SQL query builder inspired by jOOQ
"""

import sqlite3
from dataclasses import dataclass
from typing import List, Optional, Any
import click
from tabulate import tabulate


# Database Schema Models
@dataclass
class User:
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None


@dataclass
class Product:
    id: Optional[int] = None
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None


# Query Builder Classes
class QueryBuilder:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.cursor = conn.cursor()
    
    def select(self, table: str):
        return SelectQuery(self.conn, table)
    
    def insert(self, table: str):
        return InsertQuery(self.conn, table)
    
    def update(self, table: str):
        return UpdateQuery(self.conn, table)
    
    def delete(self, table: str):
        return DeleteQuery(self.conn, table)


class SelectQuery:
    def __init__(self, conn: sqlite3.Connection, table: str):
        self.conn = conn
        self.table = table
        self.columns = "*"
        self.where_clause = ""
        self.order_clause = ""
        self.limit_clause = ""
        self.params = []
    
    def fields(self, *fields):
        self.columns = ", ".join(fields)
        return self
    
    def where(self, condition: str, *params):
        self.where_clause = f"WHERE {condition}"
        self.params.extend(params)
        return self
    
    def order_by(self, *fields):
        self.order_clause = f"ORDER BY {', '.join(fields)}"
        return self
    
    def limit(self, count: int):
        self.limit_clause = f"LIMIT {count}"
        return self
    
    def fetch(self) -> List[tuple]:
        query = f"SELECT {self.columns} FROM {self.table}"
        if self.where_clause:
            query += f" {self.where_clause}"
        if self.order_clause:
            query += f" {self.order_clause}"
        if self.limit_clause:
            query += f" {self.limit_clause}"
        
        cursor = self.conn.cursor()
        cursor.execute(query, self.params)
        return cursor.fetchall()
    
    def fetch_one(self) -> Optional[tuple]:
        results = self.limit(1).fetch()
        return results[0] if results else None


class InsertQuery:
    def __init__(self, conn: sqlite3.Connection, table: str):
        self.conn = conn
        self.table = table
        self.values_dict = {}
    
    def set(self, field: str, value: Any):
        self.values_dict[field] = value
        return self
    
    def values(self, **kwargs):
        self.values_dict.update(kwargs)
        return self
    
    def execute(self) -> int:
        fields = ", ".join(self.values_dict.keys())
        placeholders = ", ".join(["?" for _ in self.values_dict])
        query = f"INSERT INTO {self.table} ({fields}) VALUES ({placeholders})"
        
        cursor = self.conn.cursor()
        cursor.execute(query, list(self.values_dict.values()))
        self.conn.commit()
        return cursor.lastrowid


class UpdateQuery:
    def __init__(self, conn: sqlite3.Connection, table: str):
        self.conn = conn
        self.table = table
        self.set_dict = {}
        self.where_clause = ""
        self.where_params = []
    
    def set(self, field: str, value: Any):
        self.set_dict[field] = value
        return self
    
    def where(self, condition: str, *params):
        self.where_clause = f"WHERE {condition}"
        self.where_params.extend(params)
        return self
    
    def execute(self) -> int:
        set_clause = ", ".join([f"{k} = ?" for k in self.set_dict.keys()])
        query = f"UPDATE {self.table} SET {set_clause}"
        
        if self.where_clause:
            query += f" {self.where_clause}"
        
        params = list(self.set_dict.values()) + self.where_params
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount


class DeleteQuery:
    def __init__(self, conn: sqlite3.Connection, table: str):
        self.conn = conn
        self.table = table
        self.where_clause = ""
        self.params = []
    
    def where(self, condition: str, *params):
        self.where_clause = f"WHERE {condition}"
        self.params.extend(params)
        return self
    
    def execute(self) -> int:
        query = f"DELETE FROM {self.table}"
        if self.where_clause:
            query += f" {self.where_clause}"
        
        cursor = self.conn.cursor()
        cursor.execute(query, self.params)
        self.conn.commit()
        return cursor.rowcount


# Database Setup
def init_database(db_path: str = "app.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER
        )
    """)
    
    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
    """)
    
    conn.commit()
    return conn


# CLI Commands
@click.group()
@click.pass_context
def cli(ctx):
    """SQL Query Builder CLI - A jOOQ-inspired query builder for Python"""
    ctx.ensure_object(dict)
    ctx.obj['conn'] = init_database()
    ctx.obj['qb'] = QueryBuilder(ctx.obj['conn'])


@cli.command()
@click.option('--name', prompt='Name', help='User name')
@click.option('--email', prompt='Email', help='User email')
@click.option('--age', prompt='Age', type=int, help='User age')
@click.pass_context
def add_user(ctx, name, email, age):
    """Add a new user to the database"""
    qb = ctx.obj['qb']
    
    try:
        user_id = qb.insert('users').values(
            name=name,
            email=email,
            age=age
        ).execute()
        
        click.echo(f"✓ User created successfully with ID: {user_id}")
    except sqlite3.IntegrityError:
        click.echo("✗ Error: Email already exists!", err=True)


@cli.command()
@click.pass_context
def list_users(ctx):
    """List all users"""
    qb = ctx.obj['qb']
    
    users = qb.select('users').order_by('id').fetch()
    
    if users:
        headers = ['ID', 'Name', 'Email', 'Age']
        click.echo(tabulate(users, headers=headers, tablefmt='grid'))
    else:
        click.echo("No users found.")


@cli.command()
@click.argument('user_id', type=int)
@click.pass_context
def get_user(ctx, user_id):
    """Get a specific user by ID"""
    qb = ctx.obj['qb']
    
    user = qb.select('users').where('id = ?', user_id).fetch_one()
    
    if user:
        click.echo(f"\nUser Details:")
        click.echo(f"ID: {user[0]}")
        click.echo(f"Name: {user[1]}")
        click.echo(f"Email: {user[2]}")
        click.echo(f"Age: {user[3]}")
    else:
        click.echo(f"✗ User with ID {user_id} not found.", err=True)


@cli.command()
@click.argument('user_id', type=int)
@click.option('--name', help='New name')
@click.option('--email', help='New email')
@click.option('--age', type=int, help='New age')
@click.pass_context
def update_user(ctx, user_id, name, email, age):
    """Update user information"""
    qb = ctx.obj['qb']
    
    query = qb.update('users')
    
    if name:
        query.set('name', name)
    if email:
        query.set('email', email)
    if age:
        query.set('age', age)
    
    rows = query.where('id = ?', user_id).execute()
    
    if rows > 0:
        click.echo(f"✓ User {user_id} updated successfully!")
    else:
        click.echo(f"✗ User with ID {user_id} not found.", err=True)


@cli.command()
@click.argument('user_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this user?')
@click.pass_context
def delete_user(ctx, user_id):
    """Delete a user"""
    qb = ctx.obj['qb']
    
    rows = qb.delete('users').where('id = ?', user_id).execute()
    
    if rows > 0:
        click.echo(f"✓ User {user_id} deleted successfully!")
    else:
        click.echo(f"✗ User with ID {user_id} not found.", err=True)


@cli.command()
@click.option('--name', prompt='Product name', help='Product name')
@click.option('--price', prompt='Price', type=float, help='Product price')
@click.option('--stock', prompt='Stock', type=int, default=0, help='Product stock')
@click.pass_context
def add_product(ctx, name, price, stock):
    """Add a new product"""
    qb = ctx.obj['qb']
    
    product_id = qb.insert('products').values(
        name=name,
        price=price,
        stock=stock
    ).execute()
    
    click.echo(f"✓ Product created successfully with ID: {product_id}")


@cli.command()
@click.pass_context
def list_products(ctx):
    """List all products"""
    qb = ctx.obj['qb']
    
    products = qb.select('products').order_by('id').fetch()
    
    if products:
        headers = ['ID', 'Name', 'Price', 'Stock']
        click.echo(tabulate(products, headers=headers, tablefmt='grid'))
    else:
        click.echo("No products found.")


@cli.command()
@click.option('--min-age', type=int, help='Minimum age filter')
@click.pass_context
def search_users(ctx, min_age):
    """Search users with filters"""
    qb = ctx.obj['qb']
    
    if min_age:
        users = qb.select('users').where('age >= ?', min_age).order_by('age').fetch()
        click.echo(f"\nUsers with age >= {min_age}:")
    else:
        users = qb.select('users').order_by('id').fetch()
        click.echo("\nAll users:")
    
    if users:
        headers = ['ID', 'Name', 'Email', 'Age']
        click.echo(tabulate(users, headers=headers, tablefmt='grid'))
    else:
        click.echo("No users found.")


if __name__ == '__main__':
    cli(obj={})
