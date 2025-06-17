import pyatv
import asyncio
import json
from pyatv.const import Protocol
import logging

DEVICE = ''
temp_device = {
    "name": "",
    "identifiers": set(),
    "pin": 0,
    "credentials": {}
}
connected_homepod = ''


# noinspection PyTypeChecker
async def scan_for_homepod(loop):
    """
    scanning for apple home devices (homepod/tv)
    :param loop: asyncio loop
    :return: returning device that areas homepod identifier
    """
    print("scanning for saved device...")
    # scanning for homepod
    homepod = await pyatv.scan(identifier=DEVICE["identifiers"], loop=loop, timeout=10)

    # printing and returning first and only result
    if homepod:
        print("found:")
        print("name: " + str(homepod[0].name) + " | type: " + str(homepod[0].device_info))
        homepod = homepod[0]
    return homepod


# noinspection PyTypeChecker
async def pair_and_save_credentials(loop, device, force_pair=False):
    """
    not needed when playing mp3 files as pyatv doesn't yet support homepod authentication over airplay
    (but does over RAOP)
    pair and connect according to specified params
    :param force_pair: force pairing in case current credentials are outdated
    :param loop: asyncio loop
    :param device: device to connect to
    :return: connected device object
    """
    global DEVICE
    pairing = 0

    # pairing a device if not paired yet
    for protocol, credentials in list(DEVICE["credentials"].items()):
        if credentials == "" or force_pair:
            print("pairing")
            pairing = await pyatv.pair(device, protocol=protocol, loop=loop)
            await pairing.begin()

            # receiving pin (Ideally only to be done on first use, can't deal with pairing when running from rockets)
            if DEVICE["pin"] == 0:
                try:
                    pin = int(input("Enter device pin: "))
                    DEVICE["pin"] = pin
                except:
                    DEVICE["pin"] = ''

            # pairing using pin
            try:
                pairing.pin(DEVICE["pin"])
                await pairing.finish()
            except Exception as e:
                print("Error, try again. Possibly incorrect pin: " + str(e))
                exit()

            await pairing.close()
            print("saving new credentials")
            DEVICE["credentials"][protocol] = pairing.service.credentials

    save_homepod_info()
    return pairing


def load_homepod_info():
    """
    deserializes json file and stores data in DEVICE variable
    :return: none
    """
    global DEVICE
    with open("homepod_info.json", "r") as device:
        DEVICE = json.load(device)
        # turning identifiers back into a set
        DEVICE["identifiers"] = set(DEVICE["identifiers"])
        # turning int values of protocol constants back into constants
        DEVICE["credentials"] = {
            Protocol(int(key)): value for key, value in DEVICE["credentials"].items()
        }


# noinspection PyTypeChecker
def save_homepod_info():
    """
    serializes DEVICE variable and stores it in file
    :return: none
    """
    temp = DEVICE.copy()
    with open("homepod_info.json", "w") as file:
        temp["identifiers"] = list(temp["identifiers"])
        # turning protocol constants into ints
        print(temp)
        temp["credentials"] = {
            key.value: value for key, value in temp["credentials"].items()
        }
        json.dump(temp, file)


async def find_and_save_new_device(loop):
    """
    scans for available devices on network and prints results
    :param loop: asyncio loop
    :return: none
    """
    global DEVICE
    devices = await pyatv.scan(loop=loop, timeout=5)

    # printing info of devices found
    index = 0
    for device in devices:
        print("index " + str(index) + ":")
        print("name: " + str(device.name) + " | type: " + str(device.device_info))
        print("identifier: " + str(device.identifier))
        print("ip address: " + str(device.address) + "\n")
        index += 1

    index = int(input("Which device (index) do you want to save to file? "))

    try:
        temp_device["name"] = devices[index].name
        temp_device["identifiers"].add(devices[index].identifier)
        # saving available protocols except companion; not needed nor supported
        for service in devices[index].services:
            if service.protocol != Protocol.Companion:
                temp_device["credentials"][service.protocol] = ""

        DEVICE = temp_device
        save_homepod_info()
        print("saved info")

    except IndexError:
        print("index out of bounds, try again")


async def play_alarm_internal(loop, file_name, volume):
    """
    plays mp3 file on homepod
    :param loop: asyncio loop
    :param file_name: name of mp3 file to play
    :type file_name: string
    :param volume: volume/100 to set homepod to
    :type volume: float
    :return:
    :rtype:
    """
    global connected_homepod

    # in case homepod wasn't connected
    if connected_homepod == '':
        await connect_and_setup_internal(loop)

    try:
        print("playing")
        await connected_homepod.audio.set_volume(volume)
        await connected_homepod.stream.stream_file(file_name)

    # if playing failed, trying to re-pair to receive new credentials
    except (pyatv.exceptions.ConnectionFailedError, pyatv.exceptions.ConnectionLostError):
        return 1

    except pyatv.exceptions.BlockedStateError:
        await connect_and_setup_internal(loop)
        await connected_homepod.audio.set_volume(volume)
        await connected_homepod.stream.stream_file(file_name)

    except Exception as e:
        print(e)

    finally:
        await asyncio.gather(*connected_homepod.close())
        return 0


async def connect_and_setup_internal(loop):
    """
    connect to saved homepod.
    instead of connecting every alarm play; which causes up to 3 seconds of delay,
    connect at the start of the script and play alarm when needed
    :return: 1 if failed, 0 if succeeded
    :rtype: int
    """
    # scan to find the correct device
    global connected_homepod
    load_homepod_info()
    homepod = await scan_for_homepod(loop)

    if not homepod:
        print("no homepod found")
        return 1

    print("homepod found")
    print("connecting")
    try:
        connected_homepod = await pyatv.connect(homepod, loop=loop)
    except asyncio.exceptions.CancelledError:
        print("failed to connect")
        return 1
    return 0


def play_alarm(alarm_file_name, volume, loop=0):
    if loop == 0:
        loop = asyncio.new_event_loop()
    loop.run_until_complete(play_alarm_internal(loop, alarm_file_name, volume))


def connect_and_setup(loop=0):
    if loop == 0:
        loop = asyncio.new_event_loop()
    loop.run_until_complete(connect_and_setup_internal(loop))


def add_new_device():
    print("--- replacing current device with new device ---")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(find_and_save_new_device(loop))
    loop.close()


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    add_new_device()
    # play_alarm("early_warning.mp3", 60)
