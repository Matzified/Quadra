import dearpygui.dearpygui as dpg
import urllib.request
import urllib.error
import threading
import string
import random
import time

# Valid characters for a Minecraft username (A-Z, a-z, 0-9, _)
VALID_CHARS = string.ascii_lowercase + string.digits + "_"

# Global Application State
is_running = False
available_names = []
total_checked = 0
attempts_target = 100
delay = 2.0

def check_username(username):
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.getcode() == 200:
                return False, "Taken"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return True, "Available"
        elif e.code == 429:
            return False, "Rate Limited"
        else:
            return False, f"Err: {e.code}"
    except Exception as e:
        return False, "Error"
    return False, "Error"

def generate_random_4_char_name():
    return "".join(random.choice(VALID_CHARS) for _ in range(4))

def search_thread():
    global is_running, total_checked, available_names
    
    while is_running and total_checked < attempts_target:
        username = generate_random_4_char_name()
        
        # Update UI: Searching status
        dpg.set_value("current_status_text", f"Checking: {username}...")
        
        is_available, status = check_username(username)
        
        if is_available:
            available_names.append(username)
            # Update UI text block
            dpg.set_value("available_list", "\n".join(available_names))
            # Save to disk
            with open("quadra_found.txt", "a") as f:
                f.write(username + "\n")
        
        total_checked += 1
        
        # Update progress and stats
        dpg.set_value("progress_bar", total_checked / attempts_target)
        dpg.set_value("stats_text", f"Checked: {total_checked} / {attempts_target} | Found: {len(available_names)}")
        
        # Enforce rate limit delay
        if status == "Rate Limited":
            dpg.set_value("current_status_text", f"Rate limited! Waiting {delay * 5}s...")
            time.sleep(delay * 5)
        else:
            time.sleep(delay)
            
    # Reset UI when done or stopped
    is_running = False
    dpg.set_value("current_status_text", "Search Finished or Stopped.")
    dpg.configure_item("start_btn", show=True)
    dpg.configure_item("stop_btn", show=False)

def start_search():
    global is_running, total_checked, attempts_target, delay, available_names
    if is_running: return
    
    attempts_target = dpg.get_value("attempts_input")
    delay = dpg.get_value("delay_input")
    
    total_checked = 0
    available_names = []
    
    # Reset UI values
    dpg.set_value("progress_bar", 0.0)
    dpg.set_value("available_list", "")
    dpg.set_value("stats_text", f"Checked: 0 / {attempts_target} | Found: 0")
    
    is_running = True
    dpg.configure_item("start_btn", show=False)
    dpg.configure_item("stop_btn", show=True)
    
    # Run the HTTP requests on a background thread so the ImGui window doesn't freeze
    threading.Thread(target=search_thread, daemon=True).start()

def stop_search():
    global is_running
    is_running = False
    dpg.set_value("current_status_text", "Stopping...")

# ==========================================
# GUI Setup
# ==========================================
dpg.create_context()
dpg.create_viewport(title='Quadra - Advanced 4-Letter Finder', width=600, height=500)
dpg.setup_dearpygui()

# Main Window
with dpg.window(label="Quadra Control Panel", width=580, height=460, pos=(5,5), no_move=True, no_resize=True, no_collapse=True):
    
    # Branding header
    dpg.add_text("QUADRA", color=(255, 85, 85)) # Cool red branding
    dpg.add_text("Advanced Minecraft Username Forger", color=(150, 150, 150))
    dpg.add_separator()
    
    dpg.add_spacer(height=5)
    
    # Input settings
    with dpg.group(horizontal=True):
        dpg.add_text("Target Attempts:")
        dpg.add_input_int(tag="attempts_input", default_value=100, width=150)
        
    with dpg.group(horizontal=True):
        dpg.add_text("Delay (Seconds):")
        dpg.add_input_float(tag="delay_input", default_value=2.0, width=150)
        
    dpg.add_spacer(height=10)
    
    # Controls
    with dpg.group(horizontal=True):
        dpg.add_button(label=" START SEARCH ", tag="start_btn", callback=start_search, width=150, height=35)
        dpg.add_button(label=" STOP SEARCH ", tag="stop_btn", callback=stop_search, width=150, height=35, show=False)
    
    dpg.add_spacer(height=10)
    dpg.add_separator()
    
    # Live Status
    dpg.add_text("Status: Waiting for input...", tag="current_status_text", color=(255, 255, 0))
    dpg.add_progress_bar(tag="progress_bar", default_value=0.0, width=-1, height=15)
    dpg.add_text("Checked: 0 / 100 | Found: 0", tag="stats_text")
    
    dpg.add_spacer(height=10)
    
    # Results Area
    dpg.add_text("Available Names Found (Saved to quadra_found.txt):", color=(100, 255, 100))
    dpg.add_input_text(tag="available_list", multiline=True, readonly=True, width=-1, height=150)
    
    # Custom Theme Styling for ImGui
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (20, 20, 25))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (45, 45, 55))
            dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 85, 85, 150))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 85, 85, 200))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 85, 85, 255))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6)
    dpg.bind_theme(global_theme)

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
