import asyncio
from utils.nas.integration import NasIntegration
from utils.nas.folder_service import NasFolderService
from utils.nas.auth_service import NasAuthService


async def main(ip_address, filter):
    nas = NasIntegration(ip_address)
    auth_service = NasAuthService(nas)
    file_service = NasFolderService(nas)
    try:
        await auth_service.login()
        reponse = await file_service.list_share()
        formatted_response = file_service.format_response(response=reponse, filter=filter)
        file_service.migrate_response(formatted_response)
    except Exception as e:
        raise e
    finally:
        await auth_service.logout()


if __name__ == "__main__":
    ip = [
            "192.168.100.101",
            "192.168.100.102",
            "192.168.100.103",
            "192.168.100.104",
            "192.168.100.105",
        ]
    for entry in ip:
        asyncio.run(main(ip_address=entry, filter="que"))

# data = [{'isdir': True, 'name': 'CPANEL_SERVER', 'path': '/CPANEL_SERVER'}, {'isdir': True, 'name': 'Data_Testing', 'path': '/Data_Testing'}, {'isdir': True, 'name': 'DATABASE_DOKUMENTASI_3', 'path': '/DATABASE_DOKUMENTASI_3'}, {'isdir': True, 'name': 'docker', 'path': '/docker'}, {'isdir': True, 'name': 'ENTERTAINMENT', 'path': '/ENTERTAINMENT'}, {'isdir': True, 'name': 'FLAMENCO', 'path': '/FLAMENCO'}, {'isdir': True, 'name': 'home', 'path': '/home'}, {'isdir': True, 'name': 'homes', 'path': '/homes'}, {'isdir': True, 'name': 'music', 'path': '/music'}, {'isdir': True, 'name': 'NetBackup', 'path': '/NetBackup'}, {'isdir': True, 'name': 'photo', 'path': '/photo'}, {'isdir': True, 'name': 'Public NAS 4', 'path': '/Public NAS 4'}, {'isdir': True, 'name': 'Queue_Job_6', 'path': '/Queue_Job_6'}, {'isdir': True, 'name': 'Queue_Job_8', 'path': '/Queue_Job_8'}, {'isdir': True, 'name': 'Queue_Job_10', 'path': '/Queue_Job_10'}, {'isdir': True, 'name': 'Queue_Job_11', 'path': '/Queue_Job_11'}, {'isdir': True, 'name': 'Queue_Job_12', 'path': '/Queue_Job_12'}, {'isdir': True, 'name': 'Render_Sequences', 'path': '/Render_Sequences'}, {'isdir': True, 'name': 'share', 'path': '/share'}, {'isdir': True, 'name': 'Sketsa PM', 'path': '/Sketsa PM'}, {'isdir': True, 'name': 'video', 'path': '/video'}, {'isdir': True, 'name': 'web', 'path': '/web'}, {'isdir': True, 'name': 'web_packages', 'path': '/web_packages'}, {'isdir': True, 'name': 'WORK DB', 'path': '/WORK DB'}]
# matching_dirs = ["//gacor/"+entry['name'] for entry in data if entry["name"].lower().startswith("que") and " " not in entry["name"]]

# print(matching_dirs)

