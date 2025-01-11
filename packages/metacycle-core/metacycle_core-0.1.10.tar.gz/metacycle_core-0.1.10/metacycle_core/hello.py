from aiohttp import web
import aiohttp_cors
import socketio
import carla
from bleak import BleakScanner

from metacycle_core.bluetooth import BLECyclingService

from rich.pretty import pprint

origins = [
    "http://localhost:1420",  # dev server run by npm tauri
    "http://127.0.0.1:62210",  # this server itself
    "tauri://localhost",  # compiled Tauri app on Linux
    "http://tauri.localhost",  # compiled Tauri app on Windows
]

sio = socketio.AsyncServer(cors_allowed_origins="*")
app = web.Application()
sio.attach(app)

# Configure permissive CORS for aiohttp
cors_options = aiohttp_cors.ResourceOptions(
    allow_credentials=True,
    expose_headers="*",
    allow_headers="*",
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)
cors = aiohttp_cors.setup(app, defaults={origin: cors_options for origin in origins})


async def index(request):
    """Serve the client-side application."""
    return web.Response(text="<h1>Hey babe</h1>", content_type="text/html")


@sio.event
def connect(sid, environ):
    print("connect ", sid)


@sio.event
async def chat_message(sid, data):
    print("message ", data)
    await sio.emit("chat_message", f"Right back at ya, {data}")


@sio.event
def disconnect(sid):
    print("disconnect ", sid)


# This is how you return a whole html site, for example.
# app.router.add_static('/static', 'static')
# app.router.add_get('/', index)


@sio.event
async def bt_discover_all(sid):
    print("Scanning all nearby bluetooth devices...")
    devices = await BleakScanner.discover(timeout=2, return_adv=True)
    for k, v in devices.items():
        ble_device, advertisement_data = v
        print(advertisement_data)
    await sio.emit("bt_discover_results", str(devices))


relevant_devices = {
    # don't use dict.from_keys with empty list as argument because it is shared
    "smart_trainer": [],
    "sterzo": [],
}


@sio.event
async def bt_discover_devices_with_relevant_services(sid):
    """
    Scans, then filters for devices that advertise characteristics that we want.
    This gives us a preliminary list of one or more devices that are relevant to us.
    The user should be presented with the results from this function.
    Frontend logic will handle selection from the list, and so on.
    """
    print("Discovering relevant devices...")
    global relevant_devices

    devices = await BleakScanner.discover(timeout=2, return_adv=True)

    # reset relevant_device list first
    for k in relevant_devices:
        relevant_devices[k] = list()

    for k, v in devices.items():
        _ble_device, advertisement_data = v
        service_uuids = advertisement_data.service_uuids

        # Careful with this logic! See BLECyclingService for how Sterzos can be correctly found.
        if (
            (BLECyclingService.ELITE.value in service_uuids)
            and (BLECyclingService.FITNESS.value not in service_uuids)
            and (BLECyclingService.POWERMETER.value not in service_uuids)
        ):
            # Just 'ELITE' is not sufficient, we need to ensure it doesnt have FTMS or powermeter.
            relevant_devices["sterzo"].append(v)
        elif (BLECyclingService.FITNESS.value in service_uuids) and (
            BLECyclingService.POWERMETER.value in service_uuids
        ):
            # We assume smart trainers have FTMS and Powermeter abilities
            relevant_devices["smart_trainer"].append(v)

    pprint(relevant_devices)

    await sio.emit(
        "bt_discover_devices_with_relevant_services_results", str(relevant_devices)
    )


carla_client = None


@sio.event
def establish_carla_client_connection(sid):
    global carla_client
    if carla_client is None:
        carla_client = carla.Client(host="127.0.0.1", port=2000, worker_threads=0)
        try:
            server_version = carla_client.get_server_version()
            print(f"Connected to carla server with version: {server_version}")
            print(f"Carla maps: {carla_client.get_available_maps()}")

        except RuntimeError:
            print("Failed to connect to carla server")
    print("Finished establishing carla client connection")


@sio.event
def sever_carla_client_connection(sid):
    global carla_client
    del carla_client
    
    # reset global variable
    carla_client = None # noqa: F841
    print("Finished severing carla client connection")


def main():
    web.run_app(app, port=62210)


if __name__ == "__main__":
    main()
