import asyncio
import settings
import sys
import time
from uuid import UUID
import requests
from twitchAPI.helper import first
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.pubsub import PubSub
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope

from models.ListenerData import ListenerData
from event_handler import CallbackEventHandler
from network_mapper import get_all_ips

scan_for_box = False

active_ips = []
connected_connections = set()
ignored_connections = set()
active = False
handler = CallbackEventHandler()


async def callback_points(uuid: UUID, data: dict) -> None:
    global handler
    print('got callback for UUID ' + str(uuid))
    reward = data["data"]["redemption"]["reward"]["title"]
    print(reward)

    data = ListenerData(**{
        "connections": connected_connections,
        "reward": reward
    })

    try:
        handler.call(data)
    except KeyError:
        pass


async def redeem_listener(APP_ID, APP_SECRET, USER_SCOPE, TARGET_CHANNEL):
    global active
    print("starting listener")
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, USER_SCOPE, force_verify=False)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, [AuthScope.CHANNEL_READ_REDEMPTIONS], refresh_token)
    user = await first(twitch.get_users(logins=[TARGET_CHANNEL]))

    pubsub = PubSub(twitch)
    pubsub.start()
    uuid = await pubsub.listen_channel_points(user.id, callback_points)
    active = True
    await ainput("Listener started! Press ENTER to stop listener\n")
    await pubsub.unlisten(uuid)
    active = False
    pubsub.stop()
    await twitch.close()


async def health_check(max_connections):
    global connected_connections
    global active_ips
    global ignored_connections
    if len(connected_connections) > max_connections:
        print("using connected lights")
        ips_to_use = connected_connections
    else:
        ips_to_use = await get_possible_lights()

    if len(connected_connections) > 0:
        to_remove = []
        for x in connected_connections:
            try:
                r = requests.get(url='http://' + x + "/healthcheck", timeout=0.2)
                time.sleep(0.1)
                print(f"{r} from {x}")
                if r.status_code == 200:
                    pass
                elif r.status_code == 404:
                    to_remove.append(x)
            except Exception:
                print("exception in health check, debug or don't. whatever.")
                pass

        for x in to_remove:
            connected_connections.remove(x)

    for x in ips_to_use:
        print(x)
        try:
            r = requests.get(url='http://' + x + "/healthcheck", timeout=0.2)
            time.sleep(0.5)
            print(f"{r} from {x}")
            if r.status_code == 200:
                connected_connections.add(x)
            elif r.status_code == 404:
                # ignored_connections.add(x)
                pass
        except Exception:
            pass


async def get_possible_lights():
    global active_ips
    global ignored_connections
    return active_ips + await get_all_ips(ignored_connections)


async def check_loop(max_connections):
    global active_ips
    global scan_for_box

    if scan_for_box:
        if len(active_ips) < max_connections:
            while True:
                print("checking health")
                await health_check(max_connections)
                await asyncio.sleep(5)


async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
        None, lambda s=string: sys.stdout.write(s + ' '))
    return await asyncio.get_event_loop().run_in_executor(
        None, sys.stdin.readline)


if __name__ == '__main__':

    lightbox_active = -1
    while lightbox_active < 0:
        try:
            lightbox_active = int(input("How many lightboxes will be connected? (0 to disable lightbox feature) \n"))
        except ValueError:
            print("Not a valid input.\n")

    try:
        loop = asyncio.new_event_loop()
        loop.create_task(redeem_listener(
            APP_ID=settings.APP_ID,
            APP_SECRET=settings.APP_SECRET,
            USER_SCOPE=settings.USER_SCOPE,
            TARGET_CHANNEL=settings.TARGET_CHANNEL
        ))

        if lightbox_active > 0:
            loop.create_task(check_loop(
                max_connections=lightbox_active
            ))
        loop.run_forever()
    except SystemExit:
        pass
