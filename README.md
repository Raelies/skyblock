<div align="left">
  
# Skyblock Auction Flipper<div align="right">UP TO DATE ✅
<br>
<div align="left">
This runs on command prompt on your computer to look for auctions that may be worth flipping. You enter in your money, min profit, and min price, and the amount of time you want this to run for. This will automaticly scan the auction house for you with no delay. You can also copy the command and open the listing by clicking the option you want in the menu that is opened.


# Dependancies
## This code requires some python extensions: <br>
1. Tkinter - installed by default on windows. <br>
1. Time - installed by default on windows. <br><br>
2. Pyperclip:
  ```sh
  pip install pyperclip
  ```
3. Requests:
  ```sh
  pip install requests
  ```
# Installation
1. Get a free API Key at [https://developer.hypixel.net/dashboard/](https://developer.hypixel.net/dashboard/)
2. Install python extensions
3. Enter your API key
   ```py
   API_KEY = 'ENTER YOUR API'
   ```
4. Adjust the request limit and time window for the requests depending on your API key
   ```py
    REQUEST_LIMIT = 300 # (Default for dev api) Limit per time you enter below
    TIME_WINDOW = 300  # (Default for dev api) enter the time reletive for the request limit in seconds
   ```
# Running the file
1. Click ```windows + r``` and enter ```cmd```
3. Run ```cd {file location}```
4. Then
  ```py
    python hypixel_flips.py
  ```
