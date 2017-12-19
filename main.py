from coconut.config import get_config
from coconut.client import client


if __name__ == '__main__':
    config = get_config()
    client.run(config.DISCORD_BOT_TOKEN)

