from models import UserTable
from database import SessionLocal
from auth import get_password_hash

db = SessionLocal()
user = UserTable(
    username="john2",
    full_name="John2 Doe",
    hashed_password=get_password_hash("secret1"),
    disabled=False
)
db.add(user)
db.commit()
db.close()

# john - secret12
# alice - secret
# john2 - secret1