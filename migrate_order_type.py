"""
Database migration script to update order type from 'Normal' to 'Regular'
Run this once to update all existing transactions
"""
import sqlite3

def migrate_order_types():
    """Update all 'Normal' order types to 'Regular'"""
    try:
        # Connect to database
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # Update all transactions with 'Normal' to 'Regular'
        cursor.execute("""
            UPDATE transactions 
            SET order_type = 'Regular' 
            WHERE order_type = 'Normal' OR order_type IS NULL
        """)
        
        rows_updated = cursor.rowcount
        conn.commit()
        
        print("Migration successful!")
        print(f"Updated {rows_updated} transactions from 'Normal' to 'Regular'")
        
        # Verify the update
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE order_type = 'Regular'")
        regular_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE order_type = 'Normal'")
        normal_count = cursor.fetchone()[0]
        
        print(f"\nCurrent status:")
        print(f"   - Regular orders: {regular_count}")
        print(f"   - Normal orders: {normal_count} (should be 0)")
        
        conn.close()
        
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    print("Starting order type migration...")
    print("   Updating 'Normal' -> 'Regular'\n")
    migrate_order_types()
