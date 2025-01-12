import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

USER_DB = os.getenv("USER_DB")
PASS_DB = os.getenv("PASS_DB")
HOST_DB = os.getenv("HOST_DB")
PORT_DB = os.getenv("PORT_DB")
NAME_DB = os.getenv("NAME_DB")


def get_engine():
    SGDB = os.getenv("SGDB")

    if SGDB == "sqlite":
        DATABASE_URL = f"sqlite:///{NAME_DB}.db"
    elif SGDB == "postgres":
        DATABASE_URL = f"postgresql://{USER_DB}:{PASS_DB}@{HOST_DB}:{PORT_DB}/{NAME_DB}"
    elif SGDB == "mysql":
        DATABASE_URL = (
            f"mysql+mysqlconnector://{USER_DB}:{PASS_DB}@{HOST_DB}:{PORT_DB}/{NAME_DB}"
        )
    else:
        raise ValueError("SGDB not supported: {SGDB}")

    return create_engine(DATABASE_URL, echo=False)
