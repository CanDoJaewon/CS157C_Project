from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from database import Neo4jDatabase
import getpass
from typing import Optional, Dict, List

class SocialNetworkUI:
    def __init__(self, console: Console, db: Neo4jDatabase):
        self.console = console
        self.db = db
        self.current_user: Optional[Dict] = None

    def register_user(self) -> None:
        self.console.print(Panel.fit("[bold green]User Registration[/bold green]"))
        
        name = Prompt.ask("Enter your full name")
        email = Prompt.ask("Enter your email")
        username = Prompt.ask("Enter your username")
        password = getpass.getpass("Enter your password: ")
        bio = Prompt.ask("Enter your bio (optional)", default="")
        
        success = self.db.create_user(name, email, username, password, bio)
        if success:
            self.console.print("[bold green]Registration successful![/bold green]")
        else:
            self.console.print("[bold red]Registration failed. Username might already exist.[/bold red]")
        
        Prompt.ask("\nPress Enter to continue...")

    def login_user(self) -> None:
        self.console.print(Panel.fit("[bold green]User Login[/bold green]"))
        
        username = Prompt.ask("Enter your username")
        password = getpass.getpass("Enter your password: ")
        
        user = self.db.authenticate_user(username, password)
        if user:
            self.current_user = user
            self.console.print(f"[bold green]Welcome back, {user['name']}![/bold green]")
        else:
            self.console.print("[bold red]Invalid username or password.[/bold red]")
        
        Prompt.ask("\nPress Enter to continue...")

    def view_profile(self) -> None:
        if not self.current_user:
            return
        
        table = Table(title="Your Profile")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Name", self.current_user["name"])
        table.add_row("Username", self.current_user["username"])
        table.add_row("Email", self.current_user["email"])
        table.add_row("Bio", self.current_user.get("bio", "No bio available"))
        
        self.console.print(table)
        Prompt.ask("\nPress Enter to continue...")

    def edit_profile(self) -> None:
        if not self.current_user:
            return
        
        self.console.print(Panel.fit("[bold green]Edit Profile[/bold green]"))
        
        name = Prompt.ask("Enter your new name", default=self.current_user["name"])
        email = Prompt.ask("Enter your new email", default=self.current_user["email"])
        bio = Prompt.ask("Enter your new bio", default=self.current_user.get("bio", ""))
        
        success = self.db.update_user(self.current_user["username"], name, email, bio)
        if success:
            self.current_user.update({"name": name, "email": email, "bio": bio})
            self.console.print("[bold green]Profile updated successfully![/bold green]")
        else:
            self.console.print("[bold red]Failed to update profile.[/bold red]")
        
        Prompt.ask("\nPress Enter to continue...")

    def follow_user(self) -> None:
        if not self.current_user:
            return
        
        username = Prompt.ask("Enter the username to follow")
        success = self.db.follow_user(self.current_user["username"], username)
        
        if success:
            self.console.print(f"[bold green]You are now following {username}[/bold green]")
        else:
            self.console.print("[bold red]Failed to follow user. User might not exist.[/bold red]")
        
        Prompt.ask("\nPress Enter to continue...")

    def unfollow_user(self) -> None:
        if not self.current_user:
            return
        
        username = Prompt.ask("Enter the username to unfollow")
        success = self.db.unfollow_user(self.current_user["username"], username)
        
        if success:
            self.console.print(f"[bold green]You have unfollowed {username}[/bold green]")
        else:
            self.console.print("[bold red]Failed to unfollow user.[/bold red]")
        
        Prompt.ask("\nPress Enter to continue...")

    def view_connections(self) -> None:
        if not self.current_user:
            return
        
        followers = self.db.get_followers(self.current_user["username"])
        following = self.db.get_following(self.current_user["username"])
        
        self._display_user_table("Your Followers", followers)
        self._display_user_table("Users You Follow", following)
        
        Prompt.ask("\nPress Enter to continue...")

    def view_mutual_connections(self) -> None:
        if not self.current_user:
            return
        
        username = Prompt.ask("Enter the username to find mutual connections with")
        mutual = self.db.get_mutual_connections(self.current_user["username"], username)
        
        self._display_user_table(f"Mutual Connections with {username}", mutual)
        Prompt.ask("\nPress Enter to continue...")

    def get_friend_recommendations(self) -> None:
        if not self.current_user:
            return
        
        recommendations = self.db.get_friend_recommendations(self.current_user["username"])
        self._display_user_table("Friend Recommendations", recommendations)
        Prompt.ask("\nPress Enter to continue...")

    def search_users(self) -> None:
        if not self.current_user:
            return
        
        query = Prompt.ask("Enter name or username to search")
        results = self.db.search_users(query)
        
        self._display_user_table("Search Results", results)
        Prompt.ask("\nPress Enter to continue...")

    def explore_popular_users(self) -> None:
        if not self.current_user:
            return
        
        popular_users = self.db.get_popular_users()
        self._display_user_table("Most Popular Users", popular_users)
        Prompt.ask("\nPress Enter to continue...")

    def view_followers(self) -> None:
        if not self.current_user:
            return
        
        followers = self.db.get_followers(self.current_user["username"])
        self._display_user_table("Your Followers", followers)
        Prompt.ask("\nPress Enter to continue...")

    def view_following(self) -> None:
        if not self.current_user:
            return
        
        following = self.db.get_following(self.current_user["username"])
        self._display_user_table("Users You Follow", following)
        Prompt.ask("\nPress Enter to continue...")

    def logout(self) -> None:
        self.current_user = None
        self.console.print("[bold green]Logged out successfully![/bold green]")
        Prompt.ask("\nPress Enter to continue...")

    def _display_user_table(self, title: str, users: List[Dict]) -> None:
        table = Table(title=title)
        table.add_column("Name", style="cyan")
        table.add_column("Username", style="green")
        table.add_column("Bio", style="yellow")
        
        for user in users:
            table.add_row(
                user["name"],
                user["username"],
                user.get("bio", "No bio available")
            )
        
        self.console.print(table) 