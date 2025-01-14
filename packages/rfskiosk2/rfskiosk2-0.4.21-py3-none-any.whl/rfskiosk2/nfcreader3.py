#!/usr/bin/python3
# -----------------------------------------------------------------------------
# Copyright 2010, 2017 Stephen Tiedemann <stephen.tiedemann@gmail.com>
#
# Licensed under the EUPL, Version 1.1 or - as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# https://joinup.ec.europa.eu/software/page/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
# -----------------------------------------------------------------------------
""" nfcreader3.py [-w [<brigadename>]]
        Reads NFC tags and sends contents to bushfire server, and plays an appropriate tone on receipt of response from server.
        Configuration details such as bushfire server name, etc. collected from ~/nfcreader.ini.
        Possible responses are:
        - member signed into an event
        - member signed out of an event
        - no events available for this member
        - invalid tag - member not recognised.
        Normally runs as a background service using systemd (NB: Environment="XDG_RUNTIME_DIR=/run/user/1000" must be set in .service file or sound will not work.)
        Built using nfcpy library, and reader needs to be setup correctly before operating - see nfcpy documentation for details.
        Currently supports Sony 380 NFC reader, though others supported by nfcpy could also be used.
        Normally runs on a Raspberry PI under Raspian, but will also run on linux systems.
        NFC reader is automatically detected on USB bus and type identified.
        Only one process can use the reader at any time.
        Central loop checks for connection to server and presence of NFC reader, and should recover from temporary loss of either.
        Uses connect/sense mode to read tags. It will read a tag as soon as it is presented, with no need to wait for release of tag first.

        Optional -w flag causes the program to enter a loop to write tags, rather than read them.

        This module is normally executed as part of nfcserver3.service, in the nfcserver3 package.
        It requires environment variables set in the following files, in order or precedence:
        # Set required env variables.
        EnvironmentFile=/etc/profile.d/rfstag/base.env
        # Allow local override of these env vars - Optional
        EnvironmentFile=-/home/pi/.config/rfstag/local.env
        Templates for these are provided in the nfcreader3 package.

"""

from __future__ import print_function
import logging
import struct
import sys
import time
import datetime
from time import asctime
import inspect
import socket
import os
import subprocess
import configparser
from dataclasses import dataclass           # , field
from timeit import default_timer as timer
from pathlib import Path

from systemd.journal import JournalHandler
import requests
import errno
import nfc, ndef
from argparse import Namespace


LOGGING_LEVEL = logging.DEBUG       # TODO change to INFO in production

if sys.version_info.major < 3:
    sys.exit("This script requires Python 3")

SYSLOG_ID = Path(__file__).stem          # 'nfcreader3'                #
log = logging.getLogger(SYSLOG_ID)

server_session = requests.Session()

######################################################################################################################


# Read external settings from .ini file, using section named for the current host

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
    package_name: str = SYSLOG_ID       #"nfcreader3"     #
    raw_version: bytes = subprocess.check_output(['/usr/bin/apt-show-versions', package_name])
    deb_version: str = str(raw_version.split(b' ')[1], 'utf-8')
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
    kiosk_version: str = deb_version
    # Get settings from external .ini file. If a section in the INI file is named after CURR_HOST, use that,
    # otherwise, use DEFAULT.
    tagging_uri: str = nset2.get('TAGGING_URI')
    checkserv_uri: str = nset2.get('CHECKSERV_URI')
    phonetag_url: str = nset2.get('PHONETAG_URI', 'bfb/phonetag')
    request_url: str = f"{scheme}://{kiosk_brigade}.{bushfire_server}/{tagging_uri}"
    checkconn_url: str = f"{scheme}://{kiosk_brigade}.{bushfire_server}/{checkserv_uri}"
    nfc_ws: str = f"ws://{kiosk_brigade}.{bushfire_server}/ws/nfc/{kiosk_brigade}/{kiosk_location}/"
    syslog_id: str = package_name                                   # Used to tag log entries in journal
    # NFC specific values
    # Assume double tag and don't send if 2 tags are read less than this (s) apart
    min_tag_gap: float = 3.0
    start_key: bytes = b'1683249127'                     # Set to any arbitrary value. Will be updated on_card_connect.
    write_brigade: str = kiosk_brigade                   # Brigade written on tags during writetags
    tag_brigade: str = kiosk_brigade                     # Used for tag emulation when phone tagging


kiosk_config = KioskConfig()

#######################################################################################################################


class RFStag_server(object):
    def __init__(self):
        # This Namespace is a hangover from the original tagtool code that used argparse.
        # It is used mainly in prepare_tt3_tag, but also emulate_tt3_tag (options.tt3_data)
        self.options = Namespace()

        self.orig_key = kiosk_config.start_key

        self.disc_time = timer()
        self.endt = timer()

        self.rtt = None

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

        self.session = server_session                   # don't remake this every time (can take ~300ms)

        # Use this flag to indicate whether a tag or a phone has been presented
        self.tag_read = False

        self.tag_brigade = None
        self.tag_issued = None
        self.tag_member = None

        self.rdwr_options = {
            'targets':      ['106A', ],                   # Only look for passive ndef tags (type A)
            'iterations':   1,                            # Reduce from default of 5 to allow faster switching to phone
            'interval':     0.1,                          # Reduce from 0.5 to improve responsiveness
            'on-startup':   self.on_startup,
            'on-discover':  self.on_discover,             # Required to quickly identify target
            'on-connect':   self.on_connect,
            'on-release':   self.on_release,       # TODO try doing without this
        }

        self.card_options = {
            'targets':      ['212F'],                # F type matches phone working as a tag reader (actually not used)
            'on-startup':   self.on_card_startup,
            'on-discover':  self.on_card_discover,
            'on-connect':   self.on_card_connect,
            'on-release':   self.on_card_release,
        }

        self.write_options = {
            'targets':      ['106A',],                          # Only look for passive ndef tags (type A)
            'on-startup':   self.on_startupw,
            'on-discover':  self.on_discoverw,                  # Required to quickly identify target
            'on-connect':   self.on_connectw,
            'on-release':   self.on_releasew,
        }

    def sendTag(self, memb, brigade, issued, tag_ts):             # Send tag data to server
        rurl = kiosk_config.request_url + str(memb)
        kbrigade = kiosk_config.kiosk_brigade
        kLoc = kiosk_config.kiosk_location

        log.info(f"memb:{str(memb)} brigade:{brigade} issued:{issued}@loc:{kLoc}")
        # TODO this should really login properly to be fully secure
        try:
            post = self.session.post(rurl, data={'tagBrigade': brigade, 'Issued': issued, 'kioskBrigade': kbrigade,
                                                 'kioskLoc': kLoc, 'tread': tag_ts}, timeout=5)  # verify=False)
        except Exception as ex:  # Catch all - may not be needed
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, type(ex).__qualname__, ex.args)
            log.error(f"POST to {rurl} failed")
            raise ValueError(f"POST to {rurl} failed")

        log.debug(f"POST result:{post.request.body}")
        log.debug(f"status:{str(post.status_code)}, reason:{post.reason}")

        if post.status_code != 200:
            log.error("Server not accepting tag")
            raise ValueError("Server not accepting tag")

        # Reader returned headers: only used to log result
        evstat =  post.headers.get('stat', 'nostat')            # Action determined by server
        m2 =      post.headers.get('member', 'norfsID')         # Member number
        mname =   post.headers.get('Mname', 'noname')           # member name

        evid =    post.headers.get('event', '0')                # Event number to sign in/out of
        evstr =   post.headers.get('evsumm', 'noevent')         # Event description
        evlist =  post.headers.get('membAvail', 'noevents')     # List of available event numbers (optional)
        evflist = post.headers.get('evDetails', 'noevents')     # List of available event descriptions (optional)

        if evlist == 'noevents':
            log.info(f"Member:{m2}={mname} evstat:{evstat} evid:{evid} evstr:{evstr}")
        else:
            log.info(f"Member:{m2}={mname} evstat:{evstat} evid:{evid} evstr:{evstr} evlist:{evlist} evflist:{evflist}")
        return post

    def getTagInfo(self, records):                              # Extract member details from tag data just read
        mdict = {}
        for index, record in enumerate(records):
            rdata = repr(record.data).split('x00')[1]           # Strip out prefix before x00
            if record.name == 'Member':
                rd2 = rdata[:-1]                                # Strip off last char which is spare closing quote
                mdict[record.name] = int(rd2)
            elif record.name == 'Issued':
                rd2 = rdata[:-2]
                mdict[record.name] = datetime.datetime.strptime(rd2, "%a %b %d  %H:%M:%S %Y")
            elif record.name == 'Brigade':                      # Only remaining one should be Brigade
                rd2 = rdata[:-2]
                mdict[record.name] = rd2
            else:
                log.error(f"{record.name}: invalid tag field : {rdata}")

        log.info(f"Tag: {mdict}")
        return mdict

    # ************************ read tags
    def on_startup(self, targets):
        log.info("** waiting for a tag **")
        log.info(inspect.currentframe().f_code.co_name)
        for target in targets:
            target.sensf_req = bytearray.fromhex("0012FC0000")          # Not really sure what this is for
        return targets

    def on_discover(self, tag):
        log.info("** on_discover **")
        tagtest1 = tag.sel_res and tag.sel_res[0] == 0x00
        tagtest2 = tag.sens_res and tag.sens_res[0] == 0x44 and tag.sens_res[1] == 0x00
        result = tagtest1 and tagtest2  # If both True, this is a tag
        log.info(f"on_rdrw_discover: result={result}  {tag}")
        self.disc_time = timer()
        return result

    def on_connect(self, tag):
        log.info("** on_connect **")
        # Tag data is available as soon as this is called
        log.info(inspect.currentframe().f_code.co_name)

        try:
            if tag.ndef is not None:
                if tag.ndef.records:
                    log.debug(tag)
                    tdata = self.getTagInfo(tag.ndef.records)
                    # Save the data from the tag so that it can be sent to the server.
                    self.tag_read = True
                    self.tag_member =  tdata['Member']
                    self.tag_brigade = tdata['Brigade']
                    self.tag_issued =  tdata['Issued']
                else:
                    log.warning("on_connect: no ndef records")
            else:
                log.warning("on_connect: no ndef")
        except Exception as inst:
            log.warning("on_connect: tag not readable")

        return False          # Return False to exit as soon as the tag is read, and don't wait for release.

    def on_release(self, tag):
        # Comes here after data has been read in on_connect.
        log.debug(inspect.currentframe().f_code.co_name)
        log.info("Ready for next tag")
        return True

    # ************************ write tags

    def on_startupw(self, targets):
        print('Please place a tag to write on the reader')
        return targets

    def on_discoverw(self, tag):
        tagtest1 = tag.sel_res and tag.sel_res[0] == 0x00
        tagtest2 = tag.sens_res and tag.sens_res[0] == 0x44 and tag.sens_res[1] == 0x00

        result = tagtest1 and tagtest2  # If both True, this is a useable tag
        if not result:
            print("Tag not writable: please replace with a suitable tag")
            time.sleep(1)

        log.info(f"on_rdrw_discoverw: result={result}  {tag}")
        return result

    def on_connectw(self, tag):
        print(f"Tag detected {tag}")
        try:
            print('To exit, press RETURN')
            member = str(input("Member#: "))
        except SyntaxError:
            member = None

        if not member or len(member) == 0:                          # Exit writeloop if no member number provided
            print('No member number provided - finishing now.')
            sys.exit(0)

        brigade = kiosk_config.write_brigade
        tstamp = asctime()

        mrec = ndef.SmartposterRecord(member)
        mrec.name = "Member"
        brec = ndef.SmartposterRecord(brigade)
        brec.name = "Brigade"
        trec = ndef.SmartposterRecord(tstamp)
        trec.name = "Issued"
        tag.ndef.records = [mrec, brec, trec, ]

        print('Tag written. Please remove')

        return True                                       # This forces wait for card to be removed

    def on_releasew(self, tag):
        print('Tag removed. Next Please')

#
#####################################################################################################################
    def on_card_startup(self, target):
        log.info("** waiting for a reader **")
        target = self.prepare_tag(target)
        return target

    def on_card_discover(self, tag):
        log.info(f"card discovered: result={tag.sensf_req} {tag}")
        self.disc_time = timer()
        return True if tag.sensf_req else False

    def make_key_str(self, ts, brigade):
        # Make the url key to reflect the time of connect
        # Include a timestamp in the url key, so it can be checked as current/not expired.
        log.info(f'make_key: ts={ts}, brigade={brigade}')
        be = brigade.encode('utf-8')
        brg_sum = sum(int(ch) for ch in be)
        tag_key = brg_sum + ts
        tag_key_str = str(tag_key)
        log.info(f'make_key: brg_sum={brg_sum}, tag_key int={tag_key}, tag_key str={tag_key_str}')
        return tag_key_str

    def get_key_ts(self, key_str, brigade):
        brg_sum = sum(int(ch) for ch in brigade.encode('utf-8'))
        tag_time = int(key_str) - brg_sum
        return tag_time

    def on_card_connect(self, tag):
        log.info("card connect")

        epoch_time = int(time.time())
        new_key_str = self.make_key_str(epoch_time, kiosk_config.kiosk_brigade)

        tag_diff = abs(epoch_time - self.get_key_ts(new_key_str, kiosk_config.kiosk_brigade))
        # assert tag_diff = 0
        # log.info(f'card_connect: key_str: {new_key_str}, ts={epoch_time}, tdiff={tag_diff}')

        self.options.tt3_data = self.options.tt3_data.replace(self.orig_key, new_key_str.encode('utf-8'))
        log.debug(f"card connect: changed tag key from {self.orig_key} to {new_key_str}")
        log.debug(f"card connect: tt3_data: {self.options.tt3_data}")

        self.orig_key = new_key_str.encode('utf-8')
        return self.emulate_tag_start(tag)

    def on_card_release(self, tag):
        log.info("card released")
        self.emulate_tag_stop(tag)
        return True

    def terminate(self):
        return False

    def prepare_tag(self, target):
        return self.prepare_tt3_tag(target)

    def prepare_rfs_url(self):
        # Set up rfstag url for inclusion in the emulated tag
        tag_key = str(int(self.orig_key))

        kc = kiosk_config               # Shorthand only
        # RFSTAG_URL = f'{KIOSK_BRIGADE}.{BUSHFIRE_SERVER}/{PHONETAG_URL}/{TAG_BRIGADE}/{KIOSK_LOCATION}/{TAG_KEY}/'
        rfstag_url = f'{kc.kiosk_brigade}.{kc.bushfire_server}/{kc.phonetag_url}/{kc.tag_brigade}/{kc.kiosk_location}/{tag_key}/'

        # url_text = b'kuringai.rfstag.com/bfb/phonetag/kuringai/hom3/1683249128/'
        url_text = rfstag_url.encode('utf-8')
        return url_text

    def prepare_tt3_tag(self, target):
        tag_options = self.options

        # Set defaults here. This was taken from original tagtool, which set defaults in arg parser.
        # In almost every case, these defaults are used below.
        # It's black magic, and I don't know or want to know how it works.
        if not hasattr(tag_options, "idm"):            tag_options.idm = '03FEFFE011223344'
        if not hasattr(tag_options, "pmm"):            tag_options.pmm = '01E0000000FFFF00'
        if not hasattr(tag_options, "sys"):            tag_options.sys = '12FC'
        if not hasattr(tag_options, "bitrate"):        tag_options.bitrate = '212'
        if not hasattr(tag_options, "ver"):            tag_options.ver = 16
        if not hasattr(tag_options, "nbr"):            tag_options.nbr = 1
        if not hasattr(tag_options, "nbw"):            tag_options.nbw = 1
        if not hasattr(tag_options, "max"):            tag_options.max = None            # "maximum number of blocks (default: computed)"
        if not hasattr(tag_options, "rfu"):            tag_options.rfu = 0
        if not hasattr(tag_options, "wf"):             tag_options.wf = 0
        if not hasattr(tag_options, "rw"):             tag_options.rw = 1
        if not hasattr(tag_options, "crc"):            tag_options.crc = None            # "checksum attribute value (default: computed)"

        if not hasattr(tag_options, "tagtype"):        tag_options.tagtype = 'tt3'
        if not hasattr(tag_options, "size"):           tag_options.size = 1024

        # Prepare the block preceding the url, including payload size (ubase2 below)
        url_text = self.prepare_rfs_url()
        ulen = len(url_text) + 1
        ubase1 = b'\xd1\x01'
        ubase2 = ulen.to_bytes(1, 'big')                    # Assume for now that the url length will fit in one byte
        ubase3 = b'\x55\x04'
        url_base = ubase1 + ubase2 + ubase3

#       self.options.data = b'\xd1\x01;U\x04kuringai.rfstag.org/bfb/phonetag/kuringai/hom3/1683249128/'
        tag_options.data = url_base + url_text

        if not (hasattr(tag_options, "tt3_data")):
            ndef_data_size = len(tag_options.data)
            ndef_area_size = ((ndef_data_size + 15) // 16) * 16
            ndef_area_size = max(ndef_area_size, tag_options.size)
            ndef_data_area = bytearray(tag_options.data) + bytearray(ndef_area_size - ndef_data_size)

            # create attribute data
            attribute_data = bytearray(16)
            attribute_data[0] = tag_options.ver
            attribute_data[1] = tag_options.nbr
            attribute_data[2] = tag_options.nbw
            if tag_options.max is None:
                nmaxb = len(ndef_data_area) // 16
            else:
                nmaxb = tag_options.max
            attribute_data[3:5] = struct.pack(">H", nmaxb)
            attribute_data[5:9] = 4 * [tag_options.rfu]
            attribute_data[9] = tag_options.wf
            attribute_data[10:14] = struct.pack(">I", len(tag_options.data))
            attribute_data[10] = tag_options.rw
            attribute_data[14:16] = struct.pack(">H", sum(attribute_data[:14]))
            tag_options.tt3_data = attribute_data + ndef_data_area

        idm = bytes.fromhex(tag_options.idm)
        pmm = bytes.fromhex(tag_options.pmm)
        _sys = bytes.fromhex(tag_options.sys)

        target.brty = tag_options.bitrate + "F"
        target.sensf_res = b"\x01" + idm + pmm + _sys

        log.debug(f'prepare_tt3_tag options: {tag_options}')
        log.debug(f'prepare_tt3_tag target: {target}')
        return target

    def emulate_tag_start(self, tag):
        return self.emulate_tt3_tag(tag)

    def emulate_tag_stop(self, tag):
        return

    def emulate_tt3_tag(self, tag):
        def ndef_read(block_number, rb, re):
            log.debug("tt3 read block #{0}".format(block_number))
            if block_number < len(self.options.tt3_data) / 16:
                first, last = block_number * 16, (block_number + 1) * 16
                block_data = self.options.tt3_data[first:last]
                return block_data

        def ndef_write(block_number, block_data, wb, we):
            log.debug("tt3 write block #{0}".format(block_number))
            if block_number < len(self.options.tt3_data) / 16:
                first, last = block_number * 16, (block_number + 1) * 16
                self.options.tt3_data[first:last] = block_data
                return True

        tag.add_service(0x0009, ndef_read, ndef_write)
        tag.add_service(0x000B, ndef_read, lambda: False)
        return True

    def run_once(self, nfc_options):
        devices = ['usb']

        for path in devices:
            try:
                clf = nfc.ContactlessFrontend(path)
            except IOError as error:
                if error.errno == errno.ENODEV:
                    log.info("no contactless reader found on " + path)
                elif error.errno == errno.EACCES:
                    log.info("access denied for device with path " + path)
                elif error.errno == errno.EBUSY:
                    log.info("the reader on " + path + " is busy")
                else:
                    log.debug(repr(error) + "when trying " + path)
            else:
                log.debug("found a usable reader on " + path)
                break
        else:
            log.error("no contactless reader available")
            raise SystemExit(1)

        try:
            # Provide settings for both tag and card/phone. nfc will determine which to use base on 'targets'
            # and _discover.
            return clf.connect(**nfc_options)
        except Exception as inst:
            log.error(f"run_once failure: {inst}")
            sys.exit(1)
        finally:
            clf.close()

    def run_reader(self):
        nfc_options = {'rdwr': self.rdwr_options, 'card': self.card_options}
        while self.run_once(nfc_options):
            # ContactlessFrontEnd connection is now closed.
            # In the case of phones, the reader has emulated a tt3 style tag and sent a url to the phone,
            # which emulates a tag. No further action is required.
            # In the case of tags, the data has been read, but not yet sent to the server.
            if self.tag_read is True:                # Send the latest tag data to the server.
                log.info(f"run: tag read (now send to server): {self.tag_member}, {self.tag_brigade}, {self.tag_issued}")
                self.sendTag(self.tag_member, self.tag_brigade, self.tag_issued, datetime.datetime.now())
                self.endt = timer()
                self.rtt = self.endt - self.disc_time
                log.info(f"run: tag {kiosk_config.bushfire_server} {self.tag_brigade}:{self.tag_member} rtt:{self.rtt:.3f}")
                self.tag_read = False
            # To avoid double tags, take a short break
            time.sleep(3)
            log.info("*** RESTART ***")

    def run_writer(self):
        nfc_options = {'rdwr': self.write_options}
        while self.run_once(nfc_options):
            # To avoid double tags, take a short break
            time.sleep(1)
            log.info("*** RESTART ***")

# def main(argv=None):
#     if argv is not None:
#         writetags = '-w' in argv
#     else:
#         writetags = False

def main(argv=None):
    # Use sys.argv if no arguments are explicitly passed
    if argv is None:
        argv = sys.argv[1:]  # Exclude the script name

    # Check for '-w' in the argument list
    writetags = '-w' in argv

    if writetags:
        print("`-w` argument detected!")
    else:
        print("No `-w` argument provided.")

    rs = RFStag_server()

    try:
        if not writetags:
            rs.run_reader()
        else:
            rs.run_writer()
    except Exception as inst:
        log.error(f"main system failure: {inst}")
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv)
