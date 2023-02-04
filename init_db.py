from models import db, Tweet

if __name__ == "__main__":
    db.connect()
    db.create_tables([Tweet])
