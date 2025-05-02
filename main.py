from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
import os
from dotenv import load_dotenv
from ui import SocialNetworkUI
from database import Neo4jDatabase

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize console for rich text formatting
    console = Console()
    
    # Initialize database connection
    db = Neo4jDatabase(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    # Initialize UI
    ui = SocialNetworkUI(console, db)
    
    # Main application loop
    while True:
        console.clear()
        console.print(Panel.fit("[bold blue]Social Network Application[/bold blue]"))
        
        if not ui.current_user:
            # Not logged in
            choice = Prompt.ask(
                "\nPlease select an option:",
                choices=["1", "2", "3"],
                default="1"
            )
            
            if choice == "1":
                ui.register_user()
            elif choice == "2":
                ui.login_user()
            elif choice == "3":
                console.print("\n[bold red]Exiting application...[/bold red]")
                break
        else:
            # Logged in
            choice = Prompt.ask(
                "\nPlease select an option:",
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                default="1"
            )
            
            if choice == "1":
                ui.view_profile()
            elif choice == "2":
                ui.edit_profile()
            elif choice == "3":
                ui.follow_user()
            elif choice == "4":
                ui.unfollow_user()
            elif choice == "5":
                ui.view_connections()
            elif choice == "6":
                ui.view_mutual_connections()
            elif choice == "7":
                ui.get_friend_recommendations()
            elif choice == "8":
                ui.search_users()
            elif choice == "9":
                ui.explore_popular_users()
            elif choice == "10":
                ui.view_followers()
            elif choice == "11":
                ui.view_following()
            elif choice == "12":
                ui.logout()
                continue

if __name__ == "__main__":
    main() 