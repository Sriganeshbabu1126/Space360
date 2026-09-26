import os
import psycopg2
from app.models import Base
from sqlalchemy import create_engine

sorted_tables = [t.name for t in Base.metadata.sorted_tables]
print(",".join(sorted_tables))
