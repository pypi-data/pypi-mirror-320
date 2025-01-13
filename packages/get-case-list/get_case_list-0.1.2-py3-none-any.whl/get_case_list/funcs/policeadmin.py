import datetime
import json
import os

import requests
from dateutil import parser
from dotenv import load_dotenv

load_dotenv()


def generate_daily_report(data):
    try:
        bank_account = data.get("bank_accounts", [])
        related_cases = data.get("related_cases", [])

        bank_ids = ", ".join([itm.get("BANK_ACCOUNT", "") for itm in bank_account])
        bank_names = ", ".join([itm.get("BANK_ACCOUNT_NAME", "") for itm in bank_account])
        case_ids = ", ".join([itm.get("CASE_NO") for itm in related_cases])
        related_to_ccib = [itm.get("CASE_NO") for itm in related_cases if itm.get("ORG_NAME") and any(sub in itm.get("ORG_NAME") for sub in ["สอท.", "ตอท."])]

        request_body = {
            "caseType": "",
            "caseId": data.get("TrackingCode"),
            "tpoCaseId": data.get("TrackingCode"),
            "findBy": os.getenv("TEAM_NO", ""),
            "caseDate": "",
            "description": "",
            "longDescription": data.get("OptionalData"),
            "suggestion": [""],
            "accountId": bank_ids,
            "accountName": bank_names,
            "numberOfCaseId": f" {(len(related_cases))} ",
            "caseIds": case_ids,
            "relatedToCCIB": related_to_ccib,
            "prefixOne": os.getenv("INSPECTOR_PREFIX", ""),
            "fullNameOne": os.getenv("INSPECTOR_FULLNAME", ""),
            "positionOne": os.getenv("INSPECTOR_POSITION", ""),
            "prefixTwo": os.getenv("SUB_INSPECTOR_PREFIX", ""),
            "fullNameTwo": os.getenv("SUB_INSPECTOR_FULLNAME", ""),
            "positionTwo": os.getenv("SUB_INSPECTOR_POSITION", ""),
        }
        try:
            headers = {"Content-Type": "application/json"}

            response = requests.post("https://policeadmin.com/cyber-patrol-services/daily-report", json=request_body, headers=headers)
            response.raise_for_status()

            with open(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_daily-report.docx", "wb") as file:
                file.write(response.content)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    except Exception as e:
        print("ERROR: when trying to generate docx report")


def generate_sender_report(data):
    related_cases = data.get("related_cases", [])

    request_body = {
        "prefixOne": os.getenv("INSPECTOR_PREFIX", ""),
        "fullNameOne": os.getenv("INSPECTOR_FULLNAME", ""),
        "positionOne": os.getenv("INSPECTOR_POSITION", ""),
        "prefixTwo": os.getenv("SUB_INSPECTOR_PREFIX", ""),
        "fullNameTwo": os.getenv("SUB_INSPECTOR_FULLNAME", ""),
        "positionTwo": os.getenv("SUB_INSPECTOR_POSITION", ""),
        "prefixThree": os.getenv("SUPER_INTENDENT_PREFIX", ""),
        "fullNameThree": os.getenv("SUPER_INTENDENT_FULLNAME", ""),
        "positionThree": os.getenv("SUPER_INTENDENT_POSITION", ""),
        "caseType": data.get("CaseTypeName"),
        "caseId": data.get("TrackingCode"),
        "caseDate": data.get("SUPER_INTENDENT"),
        "relatedCase": str(len(related_cases)),
    }
    try:
        headers = {"Content-Type": "application/json"}

        response = requests.post("https://policeadmin.com/cyber-patrol-services/sender-document", json=request_body, headers=headers)
        response.raise_for_status()

        with open(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_sender-report.docx", "wb") as file:
            file.write(response.content)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
