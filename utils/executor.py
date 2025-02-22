import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from utils.logger import logging
from utils.nas import NasIntegration

if len(sys.argv) != 2:
    logging.info("Usage: python utils/executor.py <IP_ADDRESS>")
    sys.exit(1)

ip_address = sys.argv[1]

try:
    integrate = NasIntegration(ip_address=ip_address)
    sid = integrate.login()
    data = integrate.shared_folder(sid=sid)
    formatted_data = integrate.format_response(api_response=data)
    integrate.save_response()
    logging.info(f"Shared folder extraction for {ip_address} completed successfully.")
except Exception as e:
    logging.error(f"Error extracting shared folders: {e}")
    sys.exit(1)
