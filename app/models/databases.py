from supabase import create_client,Client
import os

SUPABASE_URL = os.getenv('SUPABASE_URL','https://urgjympujyzkghpshrct.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVyZ2p5bXB1anl6a2docHNocmN0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYxOTgyNTQsImV4cCI6MjA3MTc3NDI1NH0.NbuZIxH9-jTBoL9OCML0bxUlplY7pzGXA25orw9nhIo')

supabase : Client = create_client(SUPABASE_URL,SUPABASE_KEY)

