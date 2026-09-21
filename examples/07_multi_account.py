"""
07_multi_account.py: Running multiple Shad accounts concurrently using ClientManager.
"""
from aioshad import Dispatcher, F
from aioshad.client.manager import ClientManager
from aioshad.types import Message

dp = Dispatcher()


@dp.message(F.text == "!status")
async def handle_status(msg: Message, client):
    await msg.reply(f"Account active! Self GUID: {client.me}")


def main():
    manager = ClientManager(dispatcher=dp)

    # Register multiple accounts (each with its own session file)
    manager.add_client(session="account_1", phone_number="09121111111")
    manager.add_client(session="account_2", phone_number="09122222222")

    # Run all accounts in the same event loop
    manager.run_all()


if __name__ == "__main__":
    main()
