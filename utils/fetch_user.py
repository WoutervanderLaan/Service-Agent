from schemas.types import User


fake_user_db = {
    "test@test.com": {"uid": 123456, "name": "John Doe"},
    "test2@test.com": {"uid": 987654, "name": "Jane Doe"},
}


# TODO: fetch user (in stripped format) from DB to obtain user details as context
async def fetch_user(email: str) -> User | None:
    """
    Extract user from DB to provide additional context in the process of resolving the query
    """

    try:
        user_data = fake_user_db.get(email)

        if user_data:
            return User(user_data["name"], user_data["uid"], email)

    except Exception as e:
        print("Error fetching user", e)
