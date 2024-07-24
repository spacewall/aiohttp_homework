import aiohttp
import asyncio

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post("http://0.0.0.0:8080/advertisement/",
                                json={"header": "advertisement_8", "description": "description_1"}) as response:
            print(response.status)
            print(await response.text())

        async with session.get("http://0.0.0.0:8080/advertisement/1/") as response:
            print(response.status)
            print(await response.text())

        async with session.patch("http://0.0.0.0:8080/advertisement/1/", json={
            "header": "advertisement_2"
        }) as response:
            print(response.status)
            print(await response.text())

        async with session.get("http://0.0.0.0:8080/advertisement/1/") as response:
            print(response.status)
            print(await response.text())
            
        async with session.delete("http://0.0.0.0:8080/advertisement/1/") as response:
            print(response.status)
            print(await response.text())

asyncio.run(main())
