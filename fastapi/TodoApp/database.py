# pip install sqlalchemy
from sqlalchemy import create_engine  # Tạo kết nối tới cơ sở dữ liệu.
from sqlalchemy.orm import sessionmaker # Cung cấp một class để tạo phiên làm việc (session) với cơ sở dữ liệu.
from sqlalchemy.ext.declarative import declarative_base #  Được sử dụng để khai báo các lớp (model) ánh xạ tới các bảng trong cơ sở dữ liệu.

SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread':False})

SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

Base = declarative_base()