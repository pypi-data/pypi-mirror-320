import click
import httpx
import json
from colorama import Fore, Style
import axinite.tools as axtools

CATALOG = "https://raw.githubusercontent.com/jewels86/Axinite/refs/heads/main/templates/catalog.txt"
PAGE_LEN = 10

@click.command("catalog")
@click.option("-u", "--url", type=str, help="The URL of the catalog file", default=CATALOG)
def catalog(url):
    "Shows a catalog where you can download templates."
    lines = 0
    print(f"Welcome to the {Fore.RED}Axinite Template Catalog{Style.RESET_ALL}!")

    systems = {}
    meta_paths = {}
    r_catalog = httpx.get(url)
    content = r_catalog.text
    i = 0
    for line in content.splitlines():
        print(f"\033[KFetching {Fore.GREEN}{line}{Style.RESET_ALL}...", end="\r")
        if line.startswith("http") or line.startswith("https"): r = httpx.get(line)
        else: r = httpx.get(url.replace("catalog.txt", line))
        systems[i] = json.loads(r.text)
        meta_paths[i] = line
        i += 1
    print(f"Fetched {Fore.GREEN}{len(systems)}{Style.RESET_ALL} systems from {Fore.LIGHTBLUE_EX}{url}{Style.RESET_ALL}.")

    for j in range(0, PAGE_LEN):
        try:
            print(f"{Fore.BLUE}{j}{Style.RESET_ALL}: {Fore.MAGENTA}{systems[j]['name']}{Style.RESET_ALL} by {Fore.RED}{systems[j]['author']}{Style.RESET_ALL}")
            lines += 1
        except KeyError:
            break
    print(f"[0-{PAGE_LEN - 1}] View a system, [n]ext page, [r]eprint, [q]uit")
    lines += 1
    answer = click.prompt("", type=str)

    while answer.lower() != "q":
        if answer.lower() == "n":
            if lines - 1 >= len(systems):
                click.echo("No more systems to display.")
            else:
                for j in range(lines - 1, lines + PAGE_LEN - 1):
                    try:
                        print(f"{Fore.BLUE}{j}{Style.RESET_ALL}: {Fore.MAGENTA}{systems[j]['name']}{Style.RESET_ALL} by {Fore.RED}{systems[j]['author']}{Style.RESET_ALL}")
                        lines += 1
                    except KeyError:
                        break
                print(f"[0-{lines - 1}] View a system, [n]ext page, [p]revious, [r]eprint, [q]uit")
                lines += 1
        if answer.lower() == "r":
            for j in range(0, PAGE_LEN):
                try:
                    print(f"{Fore.BLUE}{j}{Style.RESET_ALL}: {Fore.MAGENTA}{systems[j]['name']}{Style.RESET_ALL} by {Fore.RED}{systems[j]['author']}{Style.RESET_ALL}")
                except KeyError:
                    break
            print(f"[0-{PAGE_LEN - 1}] View a system, [n]ext page, [r]eprint, [q]uit")
        if answer.isdigit():
            try:
                system = systems[int(answer)]

                print(f"Name: {Fore.MAGENTA}{system['name']}{Style.RESET_ALL}")
                print(f"Author: {Fore.RED}{system['author']}{Style.RESET_ALL}")
                print(f"Description: {Fore.GREEN}{system['description']}{Style.RESET_ALL}")
                print(f"License: {Fore.YELLOW}{system['license']}{Style.RESET_ALL}")

                print(f"Download? [y/n]")
                download = click.prompt(f"{system['name']}", type=str)
                if download.lower() == 'y':
                    r1 = httpx.get(url.replace("catalog.txt", system['path']))
                    r2 = httpx.get(url.replace("catalog.txt", meta_paths[int(answer)]))
                    complete = axtools.combine(r2.text, r1.text)
                    with open(system['path'], "w") as f:
                        f.write(complete)
                    print(f"{Fore.GREEN}Downloaded {system['path']}{Style.RESET_ALL}!")
                    
                    for j in range(0, PAGE_LEN):
                        try:
                            print(f"{Fore.BLUE}{j}{Style.RESET_ALL}: {Fore.MAGENTA}{systems[j]['name']}{Style.RESET_ALL} by {Fore.RED}{systems[j]['author']}{Style.RESET_ALL}")
                        except KeyError:
                            break
                    print(f"[0-{PAGE_LEN - 1}] View a system, [n]ext page, [r]eprint, [q]uit")
                    
            except KeyError:
                print(f"{Fore.RED}Invalid system index{Style.RESET_ALL}")
        answer = click.prompt("", type=str)