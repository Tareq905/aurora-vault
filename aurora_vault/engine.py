import sqlite3
import os
import re
from collections import Counter
from .config import DB_PATH
from .supervisor import stream_vault_data


STOPWORDS = {
    "The","Who","What","Where","When","Why","How",
    "Is","Was","Are","Were","Of","In","On","At",
    "And","Or","But","Though","This","That"
}


class VaultEngine:
    def __init__(self):
        self.db_file = DB_PATH
        self.table_name = "knowledge"

    def is_initialized(self):
        if not os.path.exists(self.db_file):
            return False
        try:
            conn = sqlite3.connect(self.db_file)
            count = conn.execute(
                f"SELECT count(*) FROM {self.table_name}"
            ).fetchone()[0]
            conn.close()
            return count > 0
        except:
            return False

    def initialize(self):
        conn = sqlite3.connect(self.db_file)

        conn.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        conn.execute(
            f"CREATE TABLE {self.table_name} (content TEXT)"
        )

        batch = []
        for line in stream_vault_data():
            batch.append((line,))
            if len(batch) >= 10000:
                conn.executemany(
                    f"INSERT INTO {self.table_name}(content) VALUES (?);",
                    batch
                )
                conn.commit()
                batch = []

        if batch:
            conn.executemany(
                f"INSERT INTO {self.table_name}(content) VALUES (?);",
                batch
            )
            conn.commit()

        conn.close()

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

        words = clean.replace("?", "").split()
        keyword = max(words, key=len).capitalize()

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT content FROM {self.table_name} WHERE content LIKE ? LIMIT 300",
            (f"%{keyword}%",)
        )
        rows = cursor.fetchall()
        conn.close()

        counter = Counter()

        for r in rows:
            words = re.findall(r'\b[A-Z][a-zA-Z]+\b', r[0])

            for w in words:
                if (
                    w not in STOPWORDS
                    and w.lower() != keyword.lower()
                    and len(w) > 3
                ):
                    counter[w] += 1

        # pick most frequent (real signal)
        top_entities = [w for w, _ in counter.most_common(top_k)]

        # always include main keyword first
        result = [keyword] + top_entities

        return [{"text": x} for x in result[:top_k]]