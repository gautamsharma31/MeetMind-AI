import os

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL or SUPABASE_KEY is missing from the .env file."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def test_connection():
    response = supabase.table("meetings").select("id").limit(1).execute()
    print("Supabase connection successful!")
    print("Meetings table is accessible.")


if __name__ == "__main__":
    test_connection()
