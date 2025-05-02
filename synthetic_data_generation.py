from neo4j import GraphDatabase
from faker import Faker
import random

# Initialize Faker
fake = Faker()

# Connect to the database
uri = "bolt://localhost:7687"
username = "neo4j"
password = "CS157C^Semester^Project"
driver = GraphDatabase.driver(uri, auth=(username, password))

def create_fake_user(tx, user_data):
    query = """
    MERGE (u:User {screen_name: $screen_name})
    SET u.followers = $followers,
        u.following = $following,
        u.location = $location,
        u.name = $name,
        u.profile_image_url = $profile_image_url,
        u.url = $url,
        u.username = $username,
        u.email = $email,
        u.password = $password
    """
    tx.run(query, **user_data)

def generate_user_data():
    screen_name = fake.user_name() + str(random.randint(1000, 9999))
    return {
        "followers": 0,
        "following": 0,
        "location": fake.city(),
        "name": fake.name(),
        "profile_image_url": fake.image_url(),
        "screen_name": screen_name,
        "url": fake.url(),
        "username": screen_name,
        "email": screen_name + "@gmail.com",
        "password": "abcd1234"
    }

# Create 850 new users
def create_bulk_users(n=850):
    with driver.session() as session:
        for _ in range(n):
            user_data = generate_user_data()
            session.execute_write(create_fake_user, user_data)
    print(f"{n} fake users successfully created!")

create_bulk_users(850)
driver.close()
