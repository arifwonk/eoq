from supabase import create_client
import bcrypt

supabase = create_client(URL, KEY)


def create_user(username, password, role):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    supabase.table("users").insert({
        "username": username,
        "password": hashed,
        "role": role
    }).execute()


# contoh
create_user("admin", "0099", "admin")
create_user("user1", "4567", "user")
