import urllib.request
import urllib.error
import string
import random
import time
import argparse

# Valid characters for a Minecraft username (A-Z, a-z, 0-9, _)
VALID_CHARS = string.ascii_lowercase + string.digits + "_"

def check_username(username):
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    try:
        # We add a User-Agent header so the API doesn't immediately block us
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.getcode() == 200:
                return False, "Taken (200)"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return True, "Available (404)"
        elif e.code == 429:
            return False, "Rate Limited (429)"
        else:
            return False, f"Unknown ({e.code})"
    except Exception as e:
        return False, f"Error ({e})"
    
    return False, "Unknown Error"

def generate_random_4_char_name():
    return "".join(random.choice(VALID_CHARS) for _ in range(4))

def worker_random(attempts, delay):
    available_names = []
    print(f"Starting random search for {attempts} usernames with {delay}s delay...")
    for _ in range(attempts):
        username = generate_random_4_char_name()
        is_available, status = check_username(username)
        
        if is_available:
            print(f"[+] AVAILABLE: {username}")
            with open("available_names.txt", "a") as f:
                f.write(username + "\n")
            available_names.append(username)
        elif status.startswith("Rate Limited"):
            print(f"[!] Rate limited! Waiting {delay * 5} seconds...")
            time.sleep(delay * 5)
        else:
            print(f"[-] TAKEN/UNAVAILABLE: {username} ({status})")
            
        time.sleep(delay)
        
    return available_names

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find 4-character Minecraft usernames.")
    parser.add_argument("--attempts", type=int, default=50, help="Number of random usernames to check.")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between requests to avoid rate limits.")
    args = parser.parse_args()

    available = worker_random(args.attempts, args.delay)
    
    print("\n--- Summary ---")
    print(f"Found {len(available)} available 4-letter usernames.")
    if available:
        print("These have been saved to 'available_names.txt'.")
