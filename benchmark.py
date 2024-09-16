import time
import hashlib
import psycopg2
import mysql.connector
from redis import Redis
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def query(self, key):
        pass

    @abstractmethod
    def set(self, key, value):
        pass


class RedisDB(Database):
    def connect(self):
        return Redis(host='localhost', port=6379, db=0)

    def query(self, key):
        return self.connection.get(key)

    def set(self, key, value):
        self.connection.set(key, value)

class PostgresDB(Database):
    def connect(self):
        try:
            return psycopg2.connect(
                dbname="testdb",
                user="postgres",  # Changed from "user" to "postgres"
                password="password",
                host="localhost"
            )
        except psycopg2.Error as e:
            print(f"Unable to connect to PostgreSQL: {e}")
            return None

    def query(self, key):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT value FROM test_table WHERE key = %s", (key,))
            return cursor.fetchone()[0]

    def set(self, key, value):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO test_table (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value", (key, value))
        self.connection.commit()


class MySQLDB(Database):
    def connect(self):
        try:
            return mysql.connector.connect(
                host="localhost",
                user="user",
                password="password",
                database="testdb"
            )
        except mysql.connector.Error as e:
            print(f"Unable to connect to MySQL: {e}")
            return None

    def query(self, key):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT value FROM test_table WHERE `key` = %s", (key,))
            return cursor.fetchone()[0]

    def set(self, key, value):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO test_table (`key`, value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE value = VALUES(value)", (key, value))
        self.connection.commit()


def query_db(db, key):
    start_time = time.time()
    result = db.query(key)
    end_time = time.time()
    return end_time - start_time

def compute_hash(data, hash_function):
    start_time = time.time()
    if hash_function == 'sha256':
        hashlib.sha256(data.encode()).hexdigest()
    elif hash_function == 'keccak256':
        hashlib.sha3_256(data.encode()).hexdigest()
    end_time = time.time()
    return end_time - start_time

def run_benchmark(db, hash_function):
    # Set up test data
    test_key = 'ThisIsABigTestValuePerhapsNotThatGood'
    test_value = 'test_value' * 1000  # 10000 characters
    db.set(test_key, test_value)

    # Number of iterations
    iterations = 1000

    # Test database query time
    total_query_time = 0
    for _ in range(iterations):
        total_query_time += query_db(db, test_key)
    avg_query_time = total_query_time / iterations

    # Test hash computation time
    total_hash_time = 0
    for _ in range(iterations):
        total_hash_time += compute_hash(test_value, hash_function)
    avg_hash_time = total_hash_time / iterations

    print(f"Average {db.__class__.__name__} query time: {avg_query_time:.6f} seconds")
    print(f"Average {hash_function} computation time: {avg_hash_time:.6f} seconds")

def main():
    databases = [RedisDB(), PostgresDB(), MySQLDB()]
    hash_functions = ['sha256', 'keccak256']

    for db_class in databases:
        db = db_class
        db.connection = db.connect()
        if db.connection is None:
            print(f"Skipping tests for {db.__class__.__name__} due to connection failure.")
            continue
        for hash_function in hash_functions:
            run_benchmark(db, hash_function)
        db.connection.close()

if __name__ == "__main__":
    main()
