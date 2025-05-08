import sys
import asyncio
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
from services.nas.integration import NasIntegration
from services.nas.folder_service import NasFolderService
from services.nas.auth_service import NasAuthService

IP_ADDRESS = [
    "192.168.100.101",
    "192.168.100.102",
    "192.168.100.103",
    "192.168.100.104",
    "192.168.100.105",
]

FILTER = "que"


async def process_nas(ip: str, filter: str):
    nas = NasIntegration(ip_address=ip)
    auth_service = NasAuthService(nas)
    file_service = NasFolderService(nas)
    try:
        await auth_service.login()
        reponse = await file_service.list_share()
        formatted_response = file_service.format_response(
            response=reponse, filter=filter
        )
        file_service.migrate_response(formatted_response)
    except Exception as e:
        raise e
    finally:
        await auth_service.logout()


async def main():
    tasks = [process_nas(ip, FILTER) for ip in IP_ADDRESS]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
