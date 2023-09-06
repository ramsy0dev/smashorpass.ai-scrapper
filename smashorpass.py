import os
import sys
import time
import typer
import random
import requests

from proxy import Proxy
from rich import print
from rich.console import Console
from user_agent import generate_user_agent

# Banner
BANNER = r"""
[bold green]                             .__
[bold green]  ______ _____ _____    _____|  |__  [bold white] ___________[bold red]___________    ______ ______
[bold green] /  ___//     \\__  \  /  ___/  |  \ [bold white]/  _ \_  __ \\[bold red]____ \__  \  /  ___//  ___/
[bold green] \___ \|  Y Y  \/ __ \_\___ \|   Y  [bold white](  <_> )  | \/[bold red]  |_> > __ \_\___ \ \___ \
[bold green]/____  >__|_|  (____  /____  >___|  /[bold white]\____/|__|  [bold red]|   __(____  /____  >____  >
[bold green]     \/      \/     \/     \/     \/ [bold white]            [bold red]|__|       \/     \/     \/
                                                    [bold yellow]Made by [bold green]ramsy0dev[bold white]
"""

# Constants
URL                     = "https://www.smashorpass.ai/"
ROOT_API_URL_PATH       = "https://www.smashorpass.ai/api"
IMAGES_API_URL_PATH     = f"{ROOT_API_URL_PATH}/images"
RATING_API_URL_PATH     = f"{ROOT_API_URL_PATH}/rating"

RATE_IMAGE_PAYLOAD  = {
    "imageId": None, # the id of the image
    "rating": None # PASS: 0, SMASH: 1
}
SEEN_IMAGES_PAYLOAD = {
    "seenImages": [] # A list of already seen images id
}
IMAGES_HOSTER_URL = "https://storage.googleapis.com/smash-test-images/images" # This is where all the images are saved can be retrived by adding the image name. ******.png
SAVE_IMAGES_PATH  = "./smashorpass-images"

COOKIE = "_ga=GAx.x.xxxxxxxxxx.xxxxxxxxxx; _gid=GAx.x.xxxxxxxxx.xxxxx" # For demostration purpose you may need to change this when using this script

DELAY = 3 # Delay between requests (in secondes)

# Helpers
def banner() -> None:
    """ Banner """
    print(BANNER)

class ProxyHandler (object):
    """ Handles proxy """
    proxy: Proxy
    valid_proxies: list

    def fetch(self) -> None:
        """ Fetch proxies and validate them """
        country_code = ["US", "UK"]

        self.proxy = Proxy(
            random.choice(country_code),
            validate_proxies=True
        )

        self.valid_proxies = self.proxy.proxies

    def get_random_proxy(self) -> dict:
        """ Returns a random proxy """
        current_proxy = random.choice(self.valid_proxies)
        proxy = {
            "http": f"http://{current_proxy[0]}:{current_proxy[1]}"
        }

        return proxy

# Init cli
cli = typer.Typer()

@cli.command()
def scrap_images():
    """ Scrapes all the images from smashorpass.ai """
    console         = Console()
    proxy_handler   = ProxyHandler()
    user_agent      = generate_user_agent()

    with console.status("[bold white]Fetching and validating proxies...") as status:
        # Fetching valid proxies to use
        # proxy_handler.fetch()

        # Checking if `smashorpass.ai` is up or not
        status.update(f"[bold white]Checking connectivity to [bold red]'{URL}'[bold white]...")

        headers = {
            "User-Agent": user_agent
        }

        try:
            response = requests.get(
                URL,
                headers=headers,
                # proxies=proxy_handler.get_random_proxy()
            )
        except Exception as error:
            console.log(f"[bold red][ - ] [bold white]Can't connect to [bold red]'{URL}'[bold white]. Error: {error}")

    # Scrapping all the generted images
    # each image have an that is associated with it
    # We don't need to know the image id because
    #  when we provid the `SEEN_IMAGES_PAYLOAD`
    # the server will just reponse back with an other image id
    # in addtion of it's name that we can then use to download it
    seen_images_id = []

    while True:
        user_agent = generate_user_agent()
        headers = {
            "User-Agent": user_agent,
            "Content-Type": "application/json",
            "Cookie": COOKIE #"_ga=GA1.2.1389159854.1693962943; _gid=GA1.2.628822730.16939"
        }
        # proxies = proxy_handler.get_random_proxy()
        data = SEEN_IMAGES_PAYLOAD
        data["seenImages"] = seen_images_id

        time.sleep(DELAY)

        response = requests.post(
            IMAGES_API_URL_PATH,
            params=data,
            headers=headers,
            # proxies=proxies
        ) # For some reason the METHOD is POST and not GET :)

        # In case there are no more images to show
        # the server will return 404 wich the following
        # message:
        # {
        #   error	"No data found"
        #}
        if response.status_code == 404:
            console.log(f"[bold red][ - ] [bold white]No more images are available. Server reponse: {response.json()}")
            sys.exit(0)

        # The json reponse will be like so:
        # {
        #   "imageUrl": "image-name.png",
        #   "imageId": 0
        # }

        new_image_data  = response.json()
        new_image_url   = new_image_data["imageUrl"] # This imageUrl is just the name of image that it's saved in the server
        new_image_id    = new_image_data["imageId"]

        seen_images_id.append(new_image_id)

        if new_image_url in os.listdir(SAVE_IMAGES_PATH):
            console.log(f"[bold yellow][ ! ] [bold white]Skipping image:[bold red]'{new_image_url}'[bold white]")
            continue

        # Downloading the image
        console.log(f"[bold green][ + ] [bold white]Downloading image:[bold red]'{new_image_url}'[bold white] to [bold cyan]'{SAVE_IMAGES_PATH}/{new_image_url}'[bold white]")

        with open(f"{SAVE_IMAGES_PATH}/{new_image_url}", "wb") as image:
            stream = requests.get(
                f"{IMAGES_HOSTER_URL}/{new_image_url}",
                stream=True,
            )

            chunk_size = 1024

            for chunk in stream.iter_content(chunk_size=chunk_size):
                if not chunk:
                    pass
                else:
                    image.write(chunk)

run = cli

if __name__ == "__main__":
    banner()

    # Checking for directory where all the images
    # will be saved
    if not os.path.exists(SAVE_IMAGES_PATH):
        os.mkdir(SAVE_IMAGES_PATH)

    run()
