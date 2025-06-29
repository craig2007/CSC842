import argparse
import asyncio
import os
import sys
import time
from pathlib import PurePath, PurePosixPath

from android_analyzer_common import get_logcat_logs, select_device, start_adb, MAX_WAIT_TIME, path_type
from ppadb.client_async import ClientAsync as AdbClient
import psutil
import requests

# Constants for ollama
OLLAMA_SERVICE = "/etc/systemd/system/ollama.service"
OLLAMA_API_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"
OLLAMA_TIMEOUT = 600
LOGCAT_LOG_ANALYSIS_PROMPT = "You are an expert cyber-security analyst with a familiarity of Android logcat logs. Your task is to examine each line in the provided log data and assign a score from 1 to 10 as to how critical the log entry. Return ONLY valid JSON with EXACTLY the following fields and format\n\n"
"{\n"
'  "process": "string - the name of the process that caused the log entry",\n"'
'  "log_entry": "string - the log entry",\n'
'  "summary": "string - a summary describing what the log entry means",\n'
'  "score": number - the score indicating how critical the log entry is,\n'
'  "reason": "string - the reason that the log entry was assigned the score that it was given"\n'
"}\n\n"


def start_ollama():
    if not os.path.exists(OLLAMA_SERVICE):
        raise Exception("Ollama service not found. Ollama service needs to be installed.")
    if "ollama" not in (p.name() for p in psutil.process_iter()):
        print("Starting ollama server")
        ollama = subprocess.Popen(["systemctl", "start", "ollama"])
    i = 0
    for i in range(0, MAX_WAIT_TIME):
        time.sleep(1)
        if "ollama" in (p.name() for p in psutil.process_iter()):
            break
    if i == MAX_WAIT_TIME:
        print("ERROR: ollama failed to start")
        raise Exception("ollama failed to start")

def analyze_logcat_logs_with_ollama(log_data):
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            url=OLLAMA_API_ENDPOINT,
            headers=headers,
            json={
                "model": OLLAMA_MODEL,
                "prompt": f"{LOGCAT_LOG_ANALYSIS_PROMPT}\n\n{log_data}",
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_ctx": 12000,
                },
            },
            timeout=OLLAMA_TIMEOUT,
        )
        response.raise_for_status()

        return response.json()["response"].strip()
    except Exception as e:
        print(f"Ollama failed to provide analyzed results with error {repr(e)}")
        return None

async def main():
    parser = argparse.ArgumentParser(
        prog="logcat_analyzer",
        description="A tool for obtaining logcat logs from an Android device and using an AI model to analyze the logs",
    )
    parser.add_argument("-d", "--device", default=None, help="The serial number of the Android device to be analyzed")
    parser.add_argument(
        "-o", "--outdir", type=path_type, default=PurePath(os.getcwd(), "out"), help="Directory to output results to"
    )
    args = parser.parse_args()

    try:
        start_ollama()
        start_adb()
    except Exception as e:
        print(f"Starting services failed with exception {repr(e)}")
        sys.exit(-1)

    # Connect to the ADB server
    client = AdbClient(host="127.0.0.1", port=5037)
    device = await select_device(client, args.device)

    print("Retrieving logcat logs...")
    log_data = await get_logcat_logs(device)
    print("Sending logs to ollama...")
    analyzed_log_data = analyze_logcat_logs_with_ollama(log_data)
    print(analyzed_log_data)

if __name__ == "__main__":
    asyncio.run(main())
