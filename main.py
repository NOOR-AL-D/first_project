import os
import json
import requests
import subprocess
import argparse
import time
from datetime import datetime

# =========================
# Load config
# =========================

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()

# =========================
# Logging system
# =========================

def save_log(message):
    log_file = config["log_file"]

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a") as f:
        f.write(f"{timestamp} {message}\n")

# =========================
# Clear logs
# =========================

def clear_logs():
    log_file = config["log_file"]

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, "w") as f:
        f.write("")

    print("Logs cleared!")

# =========================
# List files
# =========================

def list_files():
    result = subprocess.run(["ls"], capture_output=True, text=True)
    print(result.stdout)

    save_log("INFO Listed files")

# =========================
# API check
# =========================

def check_api(url=None):
    if url is None:
        url = config["apis"][0]

    try:
        response = requests.get(url)

        if response.status_code == 200:
            msg = f"INFO {url} is UP (200)"
        else:
            msg = f"ERROR {url} returned {response.status_code}"

    except Exception:
        msg = f"ERROR {url} is DOWN"

    print(msg)
    save_log(msg)

# =========================
# Monitoring system (Multi API)
# =========================

def monitor_api(url=None, interval=5):

    if url:
        urls = [url]
    else:
        urls = config.get("apis", [])

    if not urls:
        print("No APIs found in config")
        return

    print(f"Monitoring {len(urls)} APIs every {interval} seconds... (CTRL+C to stop)")

    try:
        while True:
            for url in urls:
                try:
                    response = requests.get(url)

                    if response.status_code == 200:
                        msg = f"INFO {url} is UP"
                    else:
                        msg = f"ERROR {url} returned {response.status_code}"

                except Exception:
                    msg = f"ERROR {url} is DOWN"

                print(msg)
                save_log(msg)

            print("-" * 40)
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

# =========================
# CLI setup
# =========================

parser = argparse.ArgumentParser(description="DevOps CLI Tool")

subparsers = parser.add_subparsers(dest="command")

subparsers.add_parser("list")
subparsers.add_parser("log")
subparsers.add_parser("clear-logs")

api_parser = subparsers.add_parser("api")
api_parser.add_argument("url", nargs="?")

monitor_parser = subparsers.add_parser("monitor")
monitor_parser.add_argument("url", nargs="?")
monitor_parser.add_argument("--interval", type=int, default=5)

args = parser.parse_args()

# =========================
# CLI logic
# =========================

if args.command == "list":
    list_files()

elif args.command == "api":
    check_api(args.url)

elif args.command == "log":
    save_log("INFO Manual log command")

elif args.command == "monitor":
    monitor_api(args.url, args.interval)

elif args.command == "clear-logs":
    clear_logs()

else:
    parser.print_help()