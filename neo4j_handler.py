from neo4j import GraphDatabase

uri = "bolt://localhost:7687" 
username = "neo4j"
password = "CS157C^Semester^Project"

driver = GraphDatabase.driver(uri, auth=(username, password))


def get_mutual_friends(user_name1, user_name2):
    query = """
    MATCH (u:User {name: $user_name1})-[:FRIENDS]->(mutual:User)<-[:FRIENDS]-(v:User {name: $user_name2})
    RETURN mutual.name AS mutual_friend
    """
    with driver.session() as session:
        result = session.run(query, user_name1=user_name1, user_name2=user_name2)
        return [record["mutual_friend"] for record in result]


def count_users():
    query = "MATCH (u:User) RETURN count(u) AS user_count"
    with driver.session() as session:
        result = session.run(query)
        record = result.single()
        return record["user_count"]


def get_followers(user_name):
    query = """
    MATCH (u:User {name: $user_name})<-[:FRIENDS]-(f:User)
    RETURN f.name AS friend_name
    """
    with driver.session() as session:
        result = session.run(query, user_name=user_name)
        return [record["friend_name"] for record in result]

def get_following(user_name):
    query = """
    MATCH (u:User {name: $user_name})-[:FRIENDS]->(f:User)
    RETURN f.name AS friend_name
    """
    with driver.session() as session:
        result = session.run(query, user_name=user_name)
        return [record["friend_name"] for record in result]


def follow(current_user, target):
    query = """
    MATCH (u:User {name: $current_user})
    MATCH (v:User {name: $target})
    MERGE (u)-[r:FRIENDS]->(v)
    """
    with driver.session() as session:
        session.run(query, current_user=current_user, target=target)
        return f"{current_user} now follows {target}"


def unfollow(current_user, target):
    query = """
    MATCH (u:User {name: $current_user})-[r:FRIENDS]->(v:User {name: $target})
    DELETE r
    """
    with driver.session() as session:
        session.run(query, current_user=current_user, target=target)
        return f"{current_user} has now unfollowed {target}"


def create_user(name, age, city):
    query = """
    MERGE (u:User {name: $name, age: $age, city: $city})
    """
    with driver.session() as session:
        session.run(query, name=name, age=age, city=city)
        return f"A new user named {name} has now been created"


def get_users_by_name(name_substring):
    query = """
    MATCH (u:User)
    WHERE toLower(u.name) CONTAINS toLower($name_substring)
    RETURN u.name as name
    """
    with driver.session() as session:
        result = session.run(query, name_substring=name_substring)
        return [record["name"] for record in result]



