from supabase import create_client, Client
import os
import json

# Supabase project URL and anon key from your auth_app/views.py
SUPABASE_URL = "https://ljmzjgzbzvlhxeuwktpu.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxqbXpqZ3pienZsaHhldXdrdHB1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQxOTYwMDUsImV4cCI6MjA1OTc3MjAwNX0.G3UxJDCwtPHDIzD-OpMqptlCwnKI9YsrCfvPJuL0WyI"

# Access token from your MCP configuration
MCP_ACCESS_TOKEN = "sbp_94cbc6586e245e44446aee210c3a5f7425e162fb"

def main():
    print("Testing Supabase connection...")

    # Initialize the Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    try:
        # Test a simple query to check connection
        print("\nAttempting to list tables...")
        # Query information schema to get table names
        response = supabase.from_("information_schema.tables").select("table_name").eq("table_schema", "public").execute()

        print("Connection successful!")
        print("Tables in database:")
        for table in response.data:
            print(f"- {table.get('table_name')}")
    except Exception as e:
        print(f"Error connecting to Supabase: {str(e)}")

if __name__ == "__main__":
    main()
