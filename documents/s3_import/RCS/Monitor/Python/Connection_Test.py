import pyodbc
import pandas as pd

server = 'we-prd-operations-kpis.database.windows.net'
database = 'tss-subscriber-prd'

conn_str = f"""
DRIVER={{ODBC Driver 17 for SQL Server}};
SERVER={server};
DATABASE={database};
Authentication=ActiveDirectoryInteractive;
Encrypt=yes;
TrustServerCertificate=no;
"""

query = """
SELECT TOP 1 *
FROM dbo.tblProblem
"""

try:
    with pyodbc.connect(conn_str) as conn:
        print("Connected successfully.")
        df = pd.read_sql(query, conn)

        # Show number of rows and sample data
        print("Rows returned:", len(df))
        print(df.head())

        # Save to Excel only if data exists
        if not df.empty:
            df.to_excel("one_problem_record.xlsx", index=False)
            print("Data exported to one_problem_record.xlsx")
        else:
            print("No data returned from the query. File not created.")

except Exception as e:
    print("Error:", e)
