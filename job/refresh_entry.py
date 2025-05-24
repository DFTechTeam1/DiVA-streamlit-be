import subprocess
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from utils.logger import logging

commands = [
    [
        'sh',
        '/home/ai/Project/DiVA-streamlit-be/scripts/run_executor.sh',
        '--path',
        '/home/ai/Project/DiVA-streamlit-be/services/nas/executor.py',
        '--staging',
    ],
    ['sh', '/home/ai/Project/DiVA-streamlit-be/scripts/run_mounter.sh'],
    [
        'sh',
        '/home/ai/Project/DiVA-streamlit-be/scripts/run_executor.sh',
        '--path',
        '/home/ai/Project/DiVA-streamlit-be/services/monitoring/extractor.py',
        '--staging',
    ],
    ['sh', '/home/ai/Project/DiVA-streamlit-be/scripts/kill_server.sh', '--port', '24000'],
    [
        'sh',
        '/home/ai/Project/DiVA-streamlit-be/scripts/run_executor.sh',
        '--path',
        '/home/ai/Project/DiVA-streamlit-be/services/custom_model/siglip.py',
        '--staging',
    ],
    ['sh', '/home/ai/Project/DiVA-streamlit-be/scripts/run_server.sh', '--staging'],
]


def run_command(cmd: list, retries: int = 3, delay: int = 5, background: bool = False) -> None:
    attempt = 0
    while attempt < retries:
        logging.info(
            f'Running: {" ".join(cmd)} {"in background" if background else ""} (Attempt {attempt + 1}/{retries})'
        )
        try:
            if background:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.info('Started in background.')
                return
            else:
                result = subprocess.run(cmd, check=True, text=True, capture_output=True)
                logging.info(result.stdout)
                return
        except subprocess.CalledProcessError as e:
            logging.error(f'Command failed: {" ".join(cmd)}')
            logging.error('STDERR:', e.stderr)
            attempt += 1
            if attempt < retries:
                logging.warning(f'Retrying in {delay} seconds...')
                time.sleep(delay)
            else:
                logging.error('All retries failed.')
                sys.exit(e.returncode)


for command in commands[:-1]:
    run_command(command)

run_command(commands[-1], background=True)
