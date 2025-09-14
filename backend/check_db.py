#!/usr/bin/env python3
import sqlite3
import os

def check_database():
    db_path = 'mitraverify_dev.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
            tables = cursor.fetchall()
            print('Tables in database:', [t[0] for t in tables])

            if 'user' in [t[0] for t in tables]:
                cursor.execute('SELECT id, username, email FROM user')
                users = cursor.fetchall()
                print('Users in database:')
                for user in users:
                    print(f'ID: {user[0]}, Username: {user[1]}, Email: {user[2]}')
            else:
                print('No user table found')

            # Also check verifications
            if 'verification' in [t[0] for t in tables]:
                cursor.execute('SELECT COUNT(*) FROM verification')
                count = cursor.fetchone()[0]
                print(f'Total verifications: {count}')

        except Exception as e:
            print(f'Error: {e}')
        finally:
            conn.close()
    else:
        print('Database file not found')

if __name__ == '__main__':
    check_database()
