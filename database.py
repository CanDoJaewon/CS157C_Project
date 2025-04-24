from neo4j import GraphDatabase
from typing import Optional, Dict, List
import hashlib
import os

class Neo4jDatabase:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._create_constraints()

    def _create_constraints(self) -> None:
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT user_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE")
            session.run("CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE")

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, name: str, email: str, username: str, password: str, bio: str = "") -> bool:
        with self.driver.session() as session:
            try:
                result = session.run(
                    """
                    CREATE (u:User {
                        name: $name,
                        email: $email,
                        username: $username,
                        password: $password,
                        bio: $bio
                    })
                    RETURN u
                    """,
                    name=name,
                    email=email,
                    username=username,
                    password=self._hash_password(password),
                    bio=bio
                )
                return result.single() is not None
            except Exception:
                return False

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {username: $username, password: $password})
                RETURN u
                """,
                username=username,
                password=self._hash_password(password)
            )
            record = result.single()
            if record:
                user = record["u"]
                return {
                    "name": user["name"],
                    "email": user["email"],
                    "username": user["username"],
                    "bio": user.get("bio", "")
                }
            return None

    def update_user(self, username: str, name: str, email: str, bio: str) -> bool:
        with self.driver.session() as session:
            try:
                result = session.run(
                    """
                    MATCH (u:User {username: $username})
                    SET u.name = $name,
                        u.email = $email,
                        u.bio = $bio
                    RETURN u
                    """,
                    username=username,
                    name=name,
                    email=email,
                    bio=bio
                )
                return result.single() is not None
            except Exception:
                return False

    def follow_user(self, follower_username: str, followed_username: str) -> bool:
        with self.driver.session() as session:
            try:
                result = session.run(
                    """
                    MATCH (follower:User {username: $follower_username})
                    MATCH (followed:User {username: $followed_username})
                    WHERE follower <> followed
                    MERGE (follower)-[r:FOLLOWS]->(followed)
                    RETURN r
                    """,
                    follower_username=follower_username,
                    followed_username=followed_username
                )
                return result.single() is not None
            except Exception:
                return False

    def unfollow_user(self, follower_username: str, followed_username: str) -> bool:
        with self.driver.session() as session:
            try:
                result = session.run(
                    """
                    MATCH (follower:User {username: $follower_username})-[r:FOLLOWS]->(followed:User {username: $followed_username})
                    DELETE r
                    RETURN count(r) as deleted
                    """,
                    follower_username=follower_username,
                    followed_username=followed_username
                )
                return result.single()["deleted"] > 0
            except Exception:
                return False

    def get_followers(self, username: str) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (follower:User)-[:FOLLOWS]->(u:User {username: $username})
                RETURN follower
                """,
                username=username
            )
            return [{
                "name": record["follower"]["name"],
                "username": record["follower"]["username"],
                "bio": record["follower"].get("bio", "")
            } for record in result]

    def get_following(self, username: str) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {username: $username})-[:FOLLOWS]->(following:User)
                RETURN following
                """,
                username=username
            )
            return [{
                "name": record["following"]["name"],
                "username": record["following"]["username"],
                "bio": record["following"].get("bio", "")
            } for record in result]

    def get_mutual_connections(self, username1: str, username2: str) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u1:User {username: $username1})-[:FOLLOWS]->(mutual:User)<-[:FOLLOWS]-(u2:User {username: $username2})
                RETURN mutual
                """,
                username1=username1,
                username2=username2
            )
            return [{
                "name": record["mutual"]["name"],
                "username": record["mutual"]["username"],
                "bio": record["mutual"].get("bio", "")
            } for record in result]

    def get_friend_recommendations(self, username: str) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {username: $username})-[:FOLLOWS]->(:User)-[:FOLLOWS]->(recommended:User)
                WHERE NOT (u)-[:FOLLOWS]->(recommended) AND u <> recommended
                RETURN recommended, count(*) as common_friends
                ORDER BY common_friends DESC
                LIMIT 10
                """,
                username=username
            )
            return [{
                "name": record["recommended"]["name"],
                "username": record["recommended"]["username"],
                "bio": record["recommended"].get("bio", "")
            } for record in result]

    def search_users(self, query: str) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User)
                WHERE u.name CONTAINS $query OR u.username CONTAINS $query
                RETURN u
                LIMIT 20
                """,
                query=query
            )
            return [{
                "name": record["u"]["name"],
                "username": record["u"]["username"],
                "bio": record["u"].get("bio", "")
            } for record in result]

    def get_popular_users(self) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User)<-[r:FOLLOWS]-(:User)
                RETURN u, count(r) as followers
                ORDER BY followers DESC
                LIMIT 10
                """
            )
            return [{
                "name": record["u"]["name"],
                "username": record["u"]["username"],
                "bio": record["u"].get("bio", "")
            } for record in result]

    def close(self) -> None:
        self.driver.close() 