from dotenv import load_dotenv
import os


SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True


# DATABASE URL
load_dotenv()
db_user = os.getenv("POSTGRESQL_USER")
db_password = os.getenv("POSTGRESQL_PW")
database_name = "trivia"
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{db_user}:{db_password}@localhost:5432/{database_name}"
)
