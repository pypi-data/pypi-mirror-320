from colorama import Fore, Style
import subprocess
import typer

app = typer.Typer

@app.command
def start():
    try:
       print(Fore.GREEN + "running lillie.config.py" + Style.BRIGHT)
       subprocess.run(["python", "lillie.config.py"], check=True)
    except:
        return RuntimeError(Fore.RED + "something went wrong" + Style.BRIGHT)

if __name__ == "__main__":
    app()