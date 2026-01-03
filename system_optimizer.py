import sqlite3
import os
import time
from datetime import datetime

class SystemOptimizer:
    def __init__(self, db_path="pos.db", receipts_dir="receipts"):
        self.db_path = db_path
        self.receipts_dir = receipts_dir

    def optimize_database(self):
        """Runs SQLite maintenance commands to optimize performance."""
        print(f"[{datetime.now()}] Starting Database Optimization...")
        if not os.path.exists(self.db_path):
            print("Database not found.")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            
            # VACUUM: Rebuilds the database file, repacking it into a minimal amount of disk space.
            print("  - Running VACUUM...")
            conn.execute("VACUUM")
            
            # ANALYZE: Gathers statistics about tables and indices to help the Query Optimizer.
            print("  - Running ANALYZE...")
            conn.execute("ANALYZE")
            
            conn.close()
            print("Database optimization completed successfully.")
        except Exception as e:
            print(f"Error optimizing database: {e}")

    def cleanup_old_receipts(self, days_to_keep=7):
        """Removes receipt images and temporary files older than specified days."""
        print(f"[{datetime.now()}] Cleaning up old receipts (older than {days_to_keep} days)...")
        if not os.path.exists(self.receipts_dir):
            print("Receipts directory not found.")
            return
            
        count = 0
        deleted_size = 0
        cutoff_time = time.time() - (days_to_keep * 86400)
        
        for filename in os.listdir(self.receipts_dir):
            file_path = os.path.join(self.receipts_dir, filename)
            if os.path.isfile(file_path):
                # Filter for image files and logs
                if filename.lower().endswith(('.bmp', '.png', '.jpg', '.txt')):
                    file_mtime = os.path.getmtime(file_path)
                    if file_mtime < cutoff_time:
                        try:
                            size = os.path.getsize(file_path)
                            os.remove(file_path)
                            count += 1
                            deleted_size += size
                        except Exception as e:
                            print(f"  - Failed to delete {filename}: {e}")
                            
        print(f"Cleanup completed. Removed {count} files ({deleted_size / 1024:.2f} KB freed).")

    def run_all(self):
        print("\n=== SYSTEM OPTIMIZER STARTED ===")
        self.optimize_database()
        self.cleanup_old_receipts(days_to_keep=7)
        print("=== SYSTEM OPTIMIZER FINISHED ===\n")

if __name__ == "__main__":
    optimizer = SystemOptimizer()
    optimizer.run_all()
    input("Press Enter to exit...")
