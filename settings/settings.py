import os
from dotenv import load_dotenv


class global_settings:

    load_dotenv()

    try:
        CONNECTION_STRING = os.getenv("DATABASE_URL")
        DATABASE_NAME = os.getenv("DBNAMEWMS")
    except KeyError as e:
        raise RuntimeError("Could not find a CONNECTION_STRING in environment") from e
