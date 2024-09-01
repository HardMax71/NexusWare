import json
import sqlite3

from src.utils import setup_logger

logger = setup_logger("offline_manager")


class OfflineManager:
    def __init__(self, db_path='offline_data.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS offline_data (
            id INTEGER PRIMARY KEY,
            endpoint TEXT,
            method TEXT,
            data TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()

    def store_offline_action(self, endpoint, method, data):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO offline_data (endpoint, method, data)
        VALUES (?, ?, ?)
        ''', (endpoint, method, json.dumps(data)))
        self.conn.commit()
        logger.info(f"Stored offline action: {endpoint} {method}")

    def get_pending_actions(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM offline_data ORDER BY timestamp')
        actions = cursor.fetchall()
        return [{'id': a[0], 'endpoint': a[1], 'method': a[2], 'data': json.loads(a[3]), 'timestamp': a[4]} for a in
                actions]

    def remove_action(self, action_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM offline_data WHERE id = ?', (action_id,))
        self.conn.commit()
        logger.info(f"Removed offline action with ID: {action_id}")

    def clear_all_actions(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM offline_data')
        self.conn.commit()
        logger.info("Cleared all offline actions")

    def close(self):
        self.conn.close()
