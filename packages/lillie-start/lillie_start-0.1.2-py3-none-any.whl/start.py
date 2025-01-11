from colorama import Fore, Style
import subprocess
import typer

app = typer.Typer()

@app.command()
def start():
    try:
        print(Fore.GREEN + "Running lillie.config.py" + Style.BRIGHT)
        subprocess.run(["python", "lillie.config.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error running script: {e}" + Style.BRIGHT)
        raise RuntimeError("Something went wrong")
    except Exception as e:
        print(Fore.RED + f"An unexpected error occurred: {e}" + Style.BRIGHT)
        raise RuntimeError("Something went wrong")

if __name__ == "__main__":
    app()