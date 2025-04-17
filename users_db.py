from models import UserInDB

# Fake DB
fake_users_db = {
    "johndoe": UserInDB(
        username="johndoe",
        full_name="John Doe",
        hashed_password="$2b$12$t86NXDB3U5dnnmQhlTSowuGVPATCkp/RUaKMlcPBNAHL/3dMDgYDu"  # Just a fake hash
    )
}
