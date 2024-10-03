import requests
import time
import pyperclip
import tkinter as tk
from tkinter import ttk
import threading

# Replace 'YOUR_API_KEY' with your actual Hypixel API key
API_KEY = 'ENTER YOUR API'
BASE_URL = 'https://api.hypixel.net/skyblock/auctions'
REQUEST_LIMIT = 300 # (Default for dev api) Limit per time you enter below
TIME_WINDOW = 300  # (Default for dev api) enter the time reletive for the request limit in seconds

def parse_number(value):
    value = value.lower()
    if 'k' in value:
        return int(float(value.replace('k', '')) * 1_000)
    elif 'm' in value:
        return int(float(value.replace('m', '')) * 1_000_000)
    elif 'b' in value:
        return int(float(value.replace('b', '')) * 1_000_000_000)
    else:
        return int(value)

# Formatting numbers to readable formats (e.g., 3.6m, 5.2b)
def format_number(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}b"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.1f}m"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}k"
    else:
        return str(value)

def get_auctions(page=0):
    try:
        response = requests.get(f'{BASE_URL}?key={API_KEY}&page={page}')
        if response.status_code == 200:
            data = response.json()
            if not data['success']:
                print(f"Error: {data['cause']}")
                return None
            return data
        else:
            print(f"Error {response.status_code}: {response.reason}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def get_average_ah_price(item_name, rarity):
    url = f'{BASE_URL}?key={API_KEY}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not data['success']:
                print(f"Error: {data['cause']}")
                return None
            total_price = 0
            count = 0
            for auction in data['auctions']:
                if auction['item_name'] == item_name and auction['tier'] == rarity:
                    total_price += auction['starting_bid']
                    count += 1
            return total_price / count if count > 0 else None
        else:
            print(f"Error {response.status_code}: {response.reason}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def find_profitable_flips(max_money, min_profit, min_price, duration, update_gui):
    page = 0
    request_count = 0
    start_time = time.time()
    end_time = start_time + duration if duration != -1 else float('inf')

    while time.time() < end_time:
        if request_count >= REQUEST_LIMIT:
            elapsed_time = time.time() - start_time
            if elapsed_time < TIME_WINDOW:
                time.sleep(TIME_WINDOW - elapsed_time)
            start_time = time.time()
            request_count = 0

        data = get_auctions(page)
        if data is None:
            break
        request_count += 1

        auctions = data['auctions']
        print(f"Processing page {page}, number of auctions: {len(auctions)}")

        for auction in auctions:
            if auction.get('bin'):
                item_name = auction['item_name']
                rarity = auction['tier']
                starting_bid = auction['starting_bid']
                auction_id = auction['uuid']

                if starting_bid > max_money or starting_bid < min_price:
                    continue

                average_ah_price = get_average_ah_price(item_name, rarity)
                if average_ah_price:
                    # Updated profit calculation
                    profit = average_ah_price - starting_bid
                    if profit >= min_profit:
                        # Update the GUI with the new profitable item
                        update_gui({
                            'item_name': item_name,
                            'rarity': rarity,
                            'profit': profit,
                            'auction_id': auction_id,
                            'starting_bid': starting_bid,
                            'average_ah_price': average_ah_price,
                            'type': 'BIN to Auction'
                        })
                        print(f"Found profitable item: {item_name} (Rarity: {rarity}), Profit: {profit}")

        if data['totalPages'] - 1 == page:
            break
        page += 1

def copy_to_clipboard(text):
    pyperclip.copy(text)

def display_profitable_items_in_real_time():
    # Create the main window
    root = tk.Tk()
    root.title("Profitable Auction Flips")

    # Make the window larger and centered
    window_width, window_height = 600, 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
    root.configure(bg="#2c3e50")

    # Scrollable frame setup
    canvas = tk.Canvas(root, bg="#34495e")
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    user_scrolled_up = False

    # Detect if the user is scrolling up
    def on_mousewheel(event):
        nonlocal user_scrolled_up
        if event.delta > 0:  # Scrolled up
            user_scrolled_up = True
        elif event.delta < 0:  # Scrolled down
            if canvas.yview()[1] == 1.0:  # Reached the bottom
                user_scrolled_up = False
        canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    def update_gui(item):
        auction_id = item['auction_id']
        command = f"/viewauction {auction_id}"

        # Create a nicely styled button for each item found in real-time
        button = tk.Button(scrollable_frame, text=f"Item: {item['item_name']} (Profit: {format_number(item['profit'])})",
                           font=("Arial", 12), bg="#1abc9c", fg="white", pady=5, padx=10,
                           command=lambda: copy_to_clipboard(command))
        button.pack(pady=10, padx=10, fill='x')

        # Auto-scroll if the user hasn't scrolled up manually
        if not user_scrolled_up:
            canvas.yview_moveto(1.0)

    def run_flipping_search():
        # Ask for user inputs
        max_money = parse_number(input("Enter the maximum amount of money you want to spend (e.g., 10m for 10 million): "))
        min_profit = parse_number(input("Enter the minimum profit you want to make (e.g., 500k for 500 thousand): "))
        min_price = parse_number(input("Enter the minimum price of items to consider (e.g., 100k for 100 thousand): "))
        duration = int(input("Enter the duration to search for profitable flips (in seconds): "))

        # Start finding profitable flips in a background thread
        flipping_thread = threading.Thread(target=find_profitable_flips,
                                           args=(max_money, min_profit, min_price, duration, update_gui))
        flipping_thread.start()

    # Start the background thread immediately
    run_flipping_search()

    # Run the GUI event loop
    root.mainloop()

if __name__ == '__main__':
    display_profitable_items_in_real_time()
