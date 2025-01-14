#!/usr/bin/python3

"""
This connects to the bushfire server by opening a websocket to the channel used by the kiosk browser.
It scans incoming messages, and if appropriate, will play a sound associated with the message.
Current sounds supported are:
     'signin'       : Member has signed in to an event
     'signout''     : Member has signed out of an event
     'noevent'      : No events are available, so sign-in is not possible
     'invalid'      : The tag is invalid, or may not be a member of this brigade
     'choose'       ; The Member needs to select from a list of events on the kiosk
Corresponding sound files must be available for this work

This module is normally executed as part of kiosk_beeper.service, in the nfcserver3 package.
It requires environment variables set in the following files, in order or precedence:
    # Set required env variables.
    EnvironmentFile=/etc/profile.d/rfstag/base.env
    # Allow local override of these env vars - Optional
    EnvironmentFile=-/home/pi/.config/rfstag/local.env
Templates for these are provided in the nfcreader3 package.

"""


import websocket
from websocket._exceptions import *
import logging
from systemd.journal import JournalHandler
import json
import socket
import os
import sys
import configparser
from dataclasses import dataclass
import simpleaudio as sa
from pathlib import Path

SOUNDS = ['signin', 'signout', 'noevent', 'invalid', 'choose']
# Map received 'stat' to a sound file
SOUNDS_MAP = {'in': 'signin', 'out': 'signout', 'choose': 'choose', 'invalid': 'invalid', 'novent': 'noevent'}

LOGGING_LEVEL = logging.DEBUG       # TODO change to INFO in production

SYSLOG_ID = Path(__file__).stem          # 'kiosk_beeper'
log = logging.getLogger(SYSLOG_ID)

# Maps incoming messages on kiosk_ channel to sound files.
STAT_MAP = {'tagIn': 'in', 'tagOut': 'out', 'choose': 'choose', 'invalid': 'invalid', 'none': 'none'}

class CaseSensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        # Override the optionxform method to prevent case folding
        return optionstr

# Read external settings from .ini file, using section named for the current host
def getSettings(curr_host, ini_file):
    # Create a ConfigParser instance
    config = CaseSensitiveConfigParser()

    # Read the .ini file
    config.read(ini_file)
    cdict = dict(config['DEFAULT'])
    return cdict

nset2 = getSettings(socket.gethostname(), os.environ.get('NFC_INI_FILE'))

@dataclass
class KioskConfig:
    # APT package details
    package_name: str = SYSLOG_ID
    # In most cases, the host name will be the brigade/tenant name, but allow for override with env var when needed.
    curr_host: str = socket.gethostname()
    # Get settings from env variables (not in .ini file).
    # All env vars (except KIOSK_BRIGADE) below MUST be set or the service will fail and exit. No defaults are provided.
    home_dir: str = os.environ.get('HOME')
    scheme: str = os.environ.get('SCHEME', 'https')
    nfc_ini_file: str = os.environ.get('NFC_INI_FILE')
    kiosk_brigade: str = os.environ.get('KIOSK_BRIGADE', curr_host)
    bushfire_server: str = os.environ.get('BUSHFIRE_SERVER')
    kiosk_location: str = os.environ.get('KIOSK_LOCATION')
    # Get settings from external .ini file. If a section in the INI file is named after CURR_HOST, use that, otherwise, use DEFAULT.
    kiosk_ws: str = f"ws://{kiosk_brigade}.{bushfire_server}/ws/kiosk/{kiosk_brigade}/{kiosk_location}/"
    # Sounds - only needed for kiosk_beeper
    sounds_dir: str = f"{home_dir}/{nset2.get('SOUNDS')}"
    wav_sample_rate: int = 44100                                    # wav files have a sample rate of 44.1KHz
    syslog_id: str = package_name                                   # Used to tag log entries in journal

kiosk_config = KioskConfig()


def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Prevent logging from propagating to the root logger, otherwise get dups in journal
        logger.propagate = 0
        loghandler = JournalHandler(SYSLOG_IDENTIFIER=kiosk_config.syslog_id)
        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d %(levelname)-5s [%(filename)s:%(lineno)s:%(funcName)s] %(message)s",
            datefmt='%H:%M:%S')
        loghandler.setFormatter(formatter)
        logger.addHandler(loghandler)
    return logger

logging.basicConfig(format="%(asctime)s.%(msecs)03d [%(name)s:%(levelname)-5s] %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S')

logger = get_logger(kiosk_config.syslog_id)
logger.setLevel(LOGGING_LEVEL)

# Set up sounds in advance so that they are loaded in memory and faster to access
slist = {}
for sn in SOUNDS:
    fullfname = f"{kiosk_config.sounds_dir}/{sn}.wav"
    slist[sn] = {'file': fullfname, }       # 'mix': mixer.Sound(fullfname)}


def playbeep(sn):
    # Load the WAV file
    try:
        logger.debug(f"play sound: aplay -q {sn['file']}")
        wave_obj = sa.WaveObject.from_wave_file(sn['file'])

        # Play the WAV file
        play_obj = wave_obj.play()

        # Wait for the file to finish playing
        play_obj.wait_done()

    except:
        logger.error('play audio failed')
        pass  # No audio available, but ignore


def main(argv=None):
    try:
        ws = websocket.create_connection(kiosk_config.kiosk_ws)
    except ConnectionRefusedError:
        logger.error(f'server {kiosk_config.kiosk_ws} not available with {ConnectionRefusedError}')
        sys.exit(1)

    while True:
        try:
            msg = json.loads(ws.recv())
        except WebSocketConnectionClosedException:
            logger.error(f'Lost connection on {kiosk_config.kiosk_ws}')
            sys.exit(1)                                     # Containing systemd service should restart after a brief delay

        msg_type = msg['text'].split(".")[0]
        msg_brigade = msg['text'].split(".")[1]
        msg_kiosk = msg.get('tagLoc', 'station')

        # Check this message is for this kiosk, and if it's a beep command, do it
        if msg_kiosk == kiosk_config.kiosk_location and msg_type == 'tagBeep':
            stat = msg.get('stat', 'ignore')

            if stat != 'ignore':
                logger.info(f'message text: {msg_type}.{msg_brigade}, stat: {stat}')
                snd = SOUNDS_MAP.get(stat, 'invalid')
                logger.info(f'stat: {stat}, sound: {snd}')
                playbeep(slist[snd])
            else:
                logger.debug(f'message text: {msg_type}.{msg_brigade}, stat: {stat}')

if __name__ == "__main__":
    main()