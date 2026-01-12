import asyncio
import aiohttp

request = 0
url = "http://hwapi.lightcatcube.com/items/2025-09-01"

async def fetch(session):
    global request  # Tell Python you're using the global variable
    async with session.get(url) as response:
        request += 1
        print(f"Request {request}: Status {response.status}")
        # Optional: Uncomment if you want to parse the response
        # return await response.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session) for _ in range(1000)]  # 100 concurrent requests
        await asyncio.gather(*tasks)

# Run the async loop continuously
while True:
    asyncio.run(main())
