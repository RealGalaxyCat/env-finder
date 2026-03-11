from datetime import datetime

from colorama import Fore
from colorama import Back

def log(message:str, level:str=f"info", end="\n"):
    levelcolor = ""

    if level.lower() == "info":
        levelcolor = f"{Back.LIGHTCYAN_EX}{Fore.BLACK}"
    elif level.lower() == "error":
        levelcolor = f"{Back.RED}{Fore.BLACK}"
    elif level.lower() == "results":
        levelcolor = f"{Back.YELLOW}{Fore.BLACK}"
    elif level.lower() == "stats":
        levelcolor = f"{Back.LIGHTGREEN_EX}{Fore.BLACK}"

    print(f"{Fore.WHITE}[{datetime.now().strftime("%H:%M:%S")}]{Fore.RESET} {levelcolor} {level.upper().ljust(10)}{Fore.RESET}{Back.RESET} {message}", end=end)
