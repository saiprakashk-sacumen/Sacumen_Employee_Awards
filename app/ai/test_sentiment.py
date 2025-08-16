# app/ai/test_sentiment.py
import sys
import os
from datetime import datetime
import psycopg2

sys.path.append(os.path.abspath("."))  # add project root to path

from app.ai.sentiment import analyze_all_nominations, load_nominations  

# ----------------------------
# Step 1: Analyze all nominations
# ----------------------------
results = analyze_all_nominations("employee_nominations.json")

# Print results
for r in results:
    print("result:::::::", r)

# ----------------------------
# Step 2: Insert into Postgres
# ----------------------------  
conn = psycopg2.connect(
    host="db",
    dbname="awards",
    user="postgres",
    password="postgres"  # must match docker-compose
)
cur = conn.cursor()

for r in results:
    cur.execute(
        """
        INSERT INTO sentiment_results 
        (nomination_id, employee_id, manager_id, sentiment_label, sentiment_score, predicted_core_value, core_value_alignment, analyzed_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            r['nomination_id'],
            r['employee_id'],
            r['manager_id'],
            r['sentiment_label'],
            r['sentiment_score'],
            r['predicted_core_value'],
            r['core_value_alignment'],
            datetime.now()
        )
    )

conn.commit()
cur.close()
conn.close()
print("Inserted all results into Postgres")
