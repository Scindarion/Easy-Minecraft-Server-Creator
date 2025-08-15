import os
import sys
import json
import shutil
import requests
import subprocess

class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
CONFIG_PATH = "config.json"
DEFAULT_CONFIG = {
    "default_ram": "4G",
    "default_server_type": "vanilla",
    "default_version": "",
    "default_port": "25565",
    "auto_accept_eula": True,
    "servers_directory": "servers"
}

def ensure_config_exists(path=CONFIG_PATH, default=DEFAULT_CONFIG):
    if not os.path.isfile(path):
        print(f"{Color.YELLOW}[INFO] Config file not found. Creating default...{Color.RESET}")
        with open(path, "w") as f:
            json.dump(default, f, indent=4)

def load_config(path=CONFIG_PATH):
    ensure_config_exists(path)
    with open(path, "r") as f:
        return json.load(f)
def edit_settings():
    config = load_config()
    print(f"{Color.CYAN}Current settings:{Color.RESET}")
    for key, value in config.items():
        print(f"{Color.YELLOW}{key}: {value}{Color.RESET}")
    for key in config:
        new_value = input(f"{Color.GREEN}Enter new value for '{key}' (or press Enter to keep '{config[key]}'): {Color.RESET}")
        if new_value.strip():
            config[key] = new_value.strip()
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
    print(f"{Color.GREEN}✅ Settings updated.{Color.RESET}")
def get_version_manifest():
    url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    response = requests.get(url)
    return response.json()

def get_latest_version(manifest):
    return manifest["latest"]["release"]
def setup_server(version, server_type, config, versions_list):
    servers_dir = config.get("servers_directory", "servers")
    os.makedirs(servers_dir, exist_ok=True)
    server_name = f"{server_type}_{version}"
    server_path = os.path.join(servers_dir, server_name)
    os.makedirs(server_path, exist_ok=True)

    version_info = next((v for v in versions_list if v["id"] == version), None)
    if not version_info:
        raise ValueError(f"Version '{version}' not found in manifest.")

    version_url = version_info["url"]
    version_data = requests.get(version_url).json()

    if server_type == "vanilla":
        jar_url = version_data["downloads"]["server"]["url"]
    elif server_type == "paper":
        paper_api = f"https://api.papermc.io/v2/projects/paper/versions/{version}"
        builds = requests.get(paper_api).json()["builds"]
        latest_build = builds[-1]
        jar_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}/downloads/paper-{version}-{latest_build}.jar"
    else:
        raise ValueError("Unsupported server type.")

    jar_path = os.path.join(server_path, "server.jar")
    with open(jar_path, "wb") as f:
        f.write(requests.get(jar_url).content)

    eula_path = os.path.join(server_path, "eula.txt")
    with open(eula_path, "w") as f:
        f.write("eula=true\n")

    print(f"{Color.GREEN}✅ Server '{server_name}' set up at '{server_path}'{Color.RESET}")
def launch_existing_server(config):
    servers_dir = config.get("servers_directory", "servers")
    if not os.path.exists(servers_dir):
        print(f"{Color.RED}No servers directory found at '{servers_dir}'.{Color.RESET}")
        return

    servers = [d for d in os.listdir(servers_dir) if os.path.isdir(os.path.join(servers_dir, d))]
    if not servers:
        print(f"{Color.YELLOW}No servers found to launch.{Color.RESET}")
        return

    print(f"{Color.CYAN}Select a server to launch:{Color.RESET}")
    for i, server in enumerate(servers, 1):
        print(f"{Color.YELLOW}{i}. {server}{Color.RESET}")

    try:
        choice = int(input(f"{Color.GREEN}Enter number (or 0 to cancel): {Color.RESET}"))
        if choice == 0:
            print("❎ Cancelled.")
            return
        selected = servers[choice - 1]
    except (ValueError, IndexError):
        print(f"{Color.RED}Invalid selection.{Color.RESET}")
        return

    path = os.path.join(servers_dir, selected)
    original_dir = os.getcwd()
    os.chdir(path)

    print(f"{Color.GREEN}🚀 Launching server '{selected}'...{Color.RESET}")
    subprocess.run(["java", "-jar", "server.jar", "nogui"])

    os.chdir(original_dir)
    print(f"{Color.YELLOW}🛑 Server '{selected}' stopped.{Color.RESET}")
    input(f"{Color.CYAN}🔙 Press Enter to return to the main menu...{Color.RESET}")

def create_new_server(config, versions_list, latest):
    version = input(f"{Color.GREEN}Enter Minecraft version (or 'latest'): {Color.RESET}").strip()
    if version == "latest":
        version = latest

    server_type = input(f"{Color.GREEN}Enter server type ('vanilla' or 'paper'): {Color.RESET}").strip().lower()
    if server_type not in ["vanilla", "paper"]:
        print(f"{Color.RED}Invalid server type.{Color.RESET}")
        return

    try:
        setup_server(version, server_type, config, versions_list)
    except Exception as e:
        print(f"{Color.RED}❌ Error: {e}{Color.RESET}")
def delete_server(config):
    servers_dir = config.get("servers_directory", "servers")
    if not os.path.exists(servers_dir):
        print(f"{Color.RED}No servers directory found at '{servers_dir}'.{Color.RESET}")
        return

    servers = [d for d in os.listdir(servers_dir) if os.path.isdir(os.path.join(servers_dir, d))]
    if not servers:
        print(f"{Color.YELLOW}No servers found to delete.{Color.RESET}")
        return

    print(f"{Color.CYAN}Select a server to delete:{Color.RESET}")
    for i, server in enumerate(servers, 1):
        print(f"{Color.YELLOW}{i}. {server}{Color.RESET}")

    try:
        choice = int(input(f"{Color.GREEN}Enter number (or 0 to cancel): {Color.RESET}"))
        if choice == 0:
            print("❎ Cancelled.")
            return
        selected = servers[choice - 1]
    except (ValueError, IndexError):
        print(f"{Color.RED}Invalid selection.{Color.RESET}")
        return

    confirm = input(f"{Color.RED}Are you sure you want to delete '{selected}'? (y/N): {Color.RESET}")
    if confirm.lower() == "y":
        path = os.path.join(servers_dir, selected)
        shutil.rmtree(path)
        print(f"{Color.GREEN}✅ Server '{selected}' deleted.{Color.RESET}")
    else:
        print("❎ Deletion cancelled.")
def main_menu_loop(config, versions_list, latest):
    while True:
        print(f"\n{Color.CYAN}=== Minecraft Server Wizard ==={Color.RESET}")
        options = [
            "Launch Existing Server",
            "Create New Server",
            "Delete Server",
            "Edit Settings",
            "Exit"
        ]
        for i, option in enumerate(options, 1):
            print(f"{Color.YELLOW}{i}. {option}{Color.RESET}")

        try:
            choice = int(input(f"{Color.GREEN}Select an option: {Color.RESET}"))
            if choice == 1:
                launch_existing_server(config)
            elif choice == 2:
                create_new_server(config, versions_list, latest)
            elif choice == 3:
                delete_server(config)
            elif choice == 4:
                edit_settings()
            elif choice == 5:
                print(f"{Color.CYAN}👋 Goodbye!{Color.RESET}")
                break
            else:
                print(f"{Color.RED}Invalid choice.{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}Please enter a number.{Color.RESET}")
if __name__ == "__main__":
    if "--settings" in sys.argv:
        edit_settings()
        sys.exit()

    config = load_config()
    manifest = get_version_manifest()
    latest = get_latest_version(manifest)
    versions_list = manifest["versions"]

    if "--menu" in sys.argv or len(sys.argv) == 1:
        main_menu_loop(config, versions_list, latest)
    else:
        args = sys.argv[1:]
        version = server_type = None

        if len(args) >= 2:
            version, server_type = args[:2]
        elif len(args) == 1:
            version = args[0]
            server_type = config.get("default_server_type", "vanilla")
        else:
            version = config.get("default_version", latest)
            server_type = config.get("default_server_type", "vanilla")

        if version == "latest":
            version = latest

        server_type = server_type.strip().lower()
        print(f"[DEBUG] server_type input: '{server_type}'")

        if server_type not in ["vanilla", "paper"]:
            print(f"{Color.RED}❌ Invalid server type '{server_type}'. Only 'vanilla' or 'paper' are supported.{Color.RESET}")
            sys.exit(1)

        try:
            setup_server(version, server_type, config, versions_list)
        except Exception as e:
            print(f"{Color.RED}❌ Error: {e}{Color.RESET}")
            sys.exit(1)

