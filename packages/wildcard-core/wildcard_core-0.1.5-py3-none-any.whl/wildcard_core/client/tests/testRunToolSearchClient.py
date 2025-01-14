from wildcard_core.models import Action
from wildcard_core.client.WildcardBaseClient import WildcardBaseClient
import asyncio

async def main():
    client = WildcardBaseClient(api_key="", index_name="newid1")
    # TODO: Add Auth
    response = await client.run_tool_with_args(Action.Gmail.THREADS_LIST, q="from:priya.globalroute@gmail.com")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())


