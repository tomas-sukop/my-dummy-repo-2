"""
Example pipeline script: ingest raw CSV data into the database.
"""

import csv
import sqlite3


DATABASE = "../pipeline.db"


def ingest(filepath):
    conn = sqlite3.connect(DATABASE)
    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            conn.execute(
                "INSERT INTO records (name, value, owner) VALUES (?, ?, ?)",
                (row["name"], row["value"], row["owner"]),
            )
    conn.commit()
    conn.close()
    print("Ingestion complete.")


if __name__ == "__main__":
    ingest("data/input.csv")
