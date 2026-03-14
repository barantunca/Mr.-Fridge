from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Geliştirme için yerel SQLite veritabanı url'si
SQLALCHEMY_DATABASE_URL = "sqlite:///./mrfridge.db"

# SQLite'ın çoklu thread (FastAPI) ile sorunsuz çalışması için check_same_thread=False yapıyoruz
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tüm modellerimizin (House, Item) miras alacağı temel sınıf
Base = declarative_base()


# Uç noktalarda (Route) veritabanı oturumu açıp kapatmak için Dependency (Bağımlılık) fonksiyonu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
