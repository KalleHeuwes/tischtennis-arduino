import asyncio
from bleak import BleakScanner

async def scan():
    devices = await BleakScanner.discover()
    for d in devices:
        print(f"Name: {d.name}, Adresse: {d.address}")

asyncio.run(scan())