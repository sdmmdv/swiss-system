import os

def get_connection_string() -> str:
    """
    Build a PostgreSQL connection string from environment variables.
    Raises ValueError if any required variable is missing.
    """
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")

    required_vars = [dbname, user, password]
    if not all(required_vars):
        raise ValueError("Missing one or more required DB environment variables (DB_NAME, DB_USER, DB_PASS).")

    conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    return conn_string
