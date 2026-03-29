import sqlite3
import os
import re
from .config import DB_PATH
from .supervisor import stream_vault_data
from .interface import get_progress_bar


class VaultEngine:
    def __init__(self):
        self.db_file = DB_PATH
        self.table_name = "knowledge"

    def is_initialized(self):
        if not os.path.exists(self.db_file):
            return False

        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
                (self.table_name,)
            )
            table_exists = cursor.fetchone()

            if not table_exists:
                conn.close()
                return False

            # Check row count
            count = cursor.execute(
                f"SELECT count(*) FROM {self.table_name}"
            ).fetchone()[0]

            conn.close()

            return count > 0  # FIXED

        except:
            return False

    def initialize(self):
        print("◌ Supervisor: Opening Knowledge Vault...")

        conn = sqlite3.connect(self.db_file)

        # PERFORMANCE BOOST
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = OFF;")
        conn.execute("PRAGMA temp_store = MEMORY;")
        conn.execute("PRAGMA cache_size = -100000;")

        conn.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        conn.execute(
            f"CREATE VIRTUAL TABLE {self.table_name} USING fts5(content, tokenize='porter');"
        )

        total = 0

        with get_progress_bar() as progress:
            task = progress.add_task(
                "Installing Knowledge Nodes...", total=None
            )

            batch = []

            for line in stream_vault_data():
                batch.append((line,))
                total += 1

                if len(batch) >= 10000:
                    conn.executemany(
                        f"INSERT INTO {self.table_name}(content) VALUES (?);",
                        batch
                    )
                    conn.commit()
                    progress.update(task, advance=len(batch))
                    batch = []

            if batch:
                conn.executemany(
                    f"INSERT INTO {self.table_name}(content) VALUES (?);",
                    batch
                )
                conn.commit()
                progress.update(task, advance=len(batch))

        conn.close()
        print(f"◌ Success: {total} records sealed in Vault.")

    def search(self, query, top_k=5):
        if not self.is_initialized():
            return []

        clean = re.sub(
            r'(?i)\b(what|is|the|of|in|and|to|a|for|tell|me|about|who|was|how)\b',
            '',
            query
        ).strip()

        if not clean:
            clean = query

        fts_query = " OR ".join(clean.split())

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        sql = f"""
        SELECT content 
        FROM {self.table_name} 
        WHERE {self.table_name} MATCH ? 
        ORDER BY rank 
        LIMIT ?
        """

        try:
            cursor.execute(sql, (fts_query, top_k))
            rows = cursor.fetchall()
            conn.close()
            return [{"text": r[0]} for r in rows]
        except:
            conn.close()
            return []