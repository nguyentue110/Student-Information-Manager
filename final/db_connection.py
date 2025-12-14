# db_connection.py - Connection Pool Pattern
"""
GIẢI THÍCH:
- Sử dụng connection pooling để tránh mở/đóng connection liên tục
- Context manager để tự động cleanup
- Error handling chi tiết
- Singleton pattern cho global connection
"""

import mysql.connector
from mysql.connector import pooling, Error
from contextlib import contextmanager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Singleton Database Connection với Connection Pooling
    
    WHY: 
    - Connection pooling giảm overhead tạo connection mới
    - Singleton đảm bảo chỉ có 1 pool trong toàn app
    - Context manager tự động cleanup resources
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        """Khởi tạo connection pool"""
        try:
            self._pool = pooling.MySQLConnectionPool(
                pool_name="student_pool",
                pool_size=5,  # Số connection tối đa
                pool_reset_session=True,
                host='localhost',
                user='root',
                password='lequyen5002',
                database='student_management',
                autocommit=False  # Tắt autocommit để control transactions
            )
            logger.info("✓ Database pool initialized successfully")
        except Error as e:
            logger.error(f"✗ Failed to create pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager để lấy connection từ pool
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students")
        """
        connection = None
        try:
            connection = self._pool.get_connection()
            yield connection
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """
        Context manager để lấy cursor trực tiếp
        
        Usage:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM students")
                results = cursor.fetchall()
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=dictionary)
            try:
                yield cursor
                conn.commit()
            except Error as e:
                conn.rollback()
                logger.error(f"Query error: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_query(self, query, params=None, fetch_one=False):
        """
        Execute SELECT query và return results
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
            fetch_one: True để fetchone(), False để fetchall()
        
        Returns:
            dict hoặc list of dict
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                if fetch_one:
                    return cursor.fetchone()
                return cursor.fetchall()
        except Error as e:
            logger.error(f"Query failed: {query[:100]}... Error: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """
        Execute INSERT/UPDATE/DELETE và return affected rows
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
        
        Returns:
            Number of affected rows
        """
        try:
            with self.get_cursor(dictionary=False) as cursor:
                cursor.execute(query, params or ())
                return cursor.rowcount
        except Error as e:
            logger.error(f"Update failed: {query[:100]}... Error: {e}")
            raise
    
    def execute_many(self, query, params_list):
        """
        Execute batch INSERT/UPDATE
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
        
        Returns:
            Number of affected rows
        """
        try:
            with self.get_cursor(dictionary=False) as cursor:
                cursor.executemany(query, params_list)
                return cursor.rowcount
        except Error as e:
            logger.error(f"Batch update failed: {e}")
            raise

# Global instance
db = DatabaseConnection()


# ============================================================
# HELPER FUNCTIONS - Các hàm tiện ích
# ============================================================

def test_connection():
    """Test database connection"""
    try:
        result = db.execute_query("SELECT 1 as test", fetch_one=True)
        if result and result.get('test') == 1:
            logger.info("✓ Database connection test passed")
            return True
    except Exception as e:
        logger.error(f"✗ Connection test failed: {e}")
    return False

def get_table_info(table_name):
    """Get column information for a table"""
    query = f"DESCRIBE {table_name}"
    return db.execute_query(query)

def check_table_exists(table_name):
    """Check if table exists in database"""
    query = """
        SELECT COUNT(*) as count 
        FROM information_schema.tables 
        WHERE table_schema = 'student_management' 
        AND table_name = %s
    """
    result = db.execute_query(query, (table_name,), fetch_one=True)
    return result and result.get('count', 0) > 0


if __name__ == "__main__":
    # Test connection
    print("Testing database connection...")
    if test_connection():
        print("✓ Connection successful!")
        
        # Test query
        students = db.execute_query("SELECT * FROM students LIMIT 5")
        print(f"Found {len(students)} students")
    else:
        print("✗ Connection failed!")