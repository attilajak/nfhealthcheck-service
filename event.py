import asyncio
import nfhealthcheck


ioloop = asyncio.new_event_loop()

ioloop.create_task(nfhealthcheck.pods())

print("run forever")
ioloop.run_forever()