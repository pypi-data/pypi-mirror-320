from atproto import Client
from httpx import Timeout
from typing import Tuple


def in_notebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def activate_bot(username: str, password: str) -> Tuple:
    """
    Activates the bot using the provided username and password

    username: The username of the account (or alternatively the email)
    password: The password of the account

    returns: The client and the profile of the logged in bot
    """
    client = Client()
    client.request._client.timeout = Timeout(120)  # Set timeout to 120 seconds

    try:
        profile = client.login(username, password)
    except Exception as e:
        print("Unfortunately, the bot was not able to login, here is why:")
        print(f"Error: {e}")
        return None, None

    print(f"Hello {profile.display_name} from Bluesky Dot Com !")
    return client, profile


def did_it_work() -> None:
    """
    Checks if the package was installed successfully
    """
    print("Yes, it is working!")
