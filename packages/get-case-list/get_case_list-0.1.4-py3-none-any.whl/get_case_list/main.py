import argparse
import datetime
import getpass
import json
import tqdm

from get_case_list.funcs.envtools import check_env
from get_case_list.funcs.auth import login
from get_case_list.funcs.apitools import (
    get_bank_account_by_case_id,
    get_case_detail_by_case_id,
    get_case_detail_by_inst_id,
    get_cases_from_api,
    get_related_cases_by_data_id,
)
from get_case_list.funcs.prompt import ask_process
from get_case_list.funcs.exceltools import create_excel_file, remove_all_files
from get_case_list.funcs.policeadmin import generate_daily_report, generate_sender_report


def fetch_case_details_and_related_cases(token, cases):
    for case_item in tqdm.tqdm(cases, desc="Fetching case detail"):
        inst_id = case_item.get("InstId")
        case_detail = get_case_detail_by_inst_id(token, inst_id) if inst_id else []
        if case_detail:
            case_item["detail"] = case_detail[0]

    for case_item in tqdm.tqdm(cases, desc="Fetching related cases"):
        data_id = case_item.get("detail", {}).get("DATA_ID", 0)
        if data_id:
            related_cases = get_related_cases_by_data_id(token, data_id)
            case_item["related_cases"] = related_cases if related_cases else []

    return [case for case in cases if case.get("related_cases")]


def process_case_details(selected_case, token):
    idx_related_case = 0
    for case in tqdm.tqdm(selected_case.get("related_cases", []), "Fetching related case with information"):
        case_id = case.get("CASE_ID", 0)
        if case_id:
            case_detail = get_case_detail_by_case_id(token, case_id)
            selected_case["related_cases"][idx_related_case] = {**case, **case_detail}
        idx_related_case += 1

    selected_case["bank_accounts"] = get_bank_account_by_case_id(token, selected_case.get("detail", {}).get("DATA_ID", 0))


def create_case_report(selected_case):
    case_informations_headers = ("เลขคดี", "จำนวนเคสที่เกี่ยวข้อง", "รายละเอียด", "Link", "Case ids ที่เกี่ยวข้อง")
    case_informations_body = [
        (
            selected_case.get("TrackingCode", ""),
            len(selected_case.get("related_cases", [])),
            selected_case.get("OptionalData", ""),
            f"(https://officer.thaipoliceonline.go.th/pct-in/officer/task-admin-view/{selected_case.get('InstId')}#task-admin)",
            ", ".join([itm.get("CASE_NO") for itm in selected_case.get("related_cases", [])]),
        )
    ]
    create_excel_file(case_informations_headers, case_informations_body, selected_case.get("TrackingCode", "selected_case"))

    related_cases_headers = ("เลขรับแจ้งความ", "ประเภท", "หน่วยงานที่รับผิดชอบ", "สถานะ", "มูลค่าความเสียหาย", "รายละเอียด")
    related_cases_body = [
        (itm.get("CASE_NO", ""), itm.get("CASE_TYPE_ABBR", ""), itm.get("ORG_NAME", ""), itm.get("COUNT_RATE", ""), itm.get("DAMAGE_VALUE", ""), itm.get("CASE_BEHAVIOR", ""))
        for itm in selected_case.get("related_cases", [])
    ]
    create_excel_file(related_cases_headers, related_cases_body, f"{selected_case.get('TrackingCode', '')}_related_cases")

    bank_account_headers = ["เลขบัญชี", "ชื่อบัญชี", "ธนาคาร"]
    bank_account_body = [(itm.get("BANK_ACCOUNT", ""), itm.get("BANK_ACCOUNT_NAME", ""), itm.get("BANK_NAME", "")) for itm in selected_case.get("bank_accounts", [])]
    create_excel_file(bank_account_headers, bank_account_body, f"{selected_case.get('TrackingCode', '')}_bank_account")


def main():
    check_env()
    parser = argparse.ArgumentParser(description="Get data from API")
    parser.add_argument("-u", "--username", required=True, help="USERNAME")
    parser.add_argument("-p", "--password", type=str, help="PASSWORD")
    parser.add_argument("-s", "--start_date", type=str, default=datetime.datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("-e", "--end_date", type=str, default=datetime.datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("-c", "--case_id", help="XXXXXX")
    parser.add_argument("-k", "--keyword", help="Keyword")
    parser.add_argument("-f", "--force", action="store_true", help="Force action without confirmation")
    parser.add_argument("-l", "--limit", type=str, default=5, help="Number of records to fetch")
    args = parser.parse_args()

    username = args.username
    password = args.password or getpass.getpass("Enter password: ")
    start_date = args.start_date
    end_date = args.end_date
    case_id = args.case_id
    keyword = args.keyword
    force = args.force
    limit = args.limit

    token = login(username, password)

    if force:
        remove_all_files()

    if token:
        if not case_id:
            print(f"INFO: start process with {username} ({start_date} - {end_date}) limit={limit}")
            cases = get_cases_from_api(token, start_date, end_date, limit, keyword)
            filtered_cases = fetch_case_details_and_related_cases(token, cases)

            filtered_cases_headers = ("เลขคดี", "จำนวนเคสที่เกี่ยวข้อง", "รายละเอียด", "Link", "Case ids ที่เกี่ยวข้อง")
            filtered_cases_body = [
                (
                    case_item.get("TrackingCode", ""),
                    len(case_item.get("related_cases", [])),
                    case_item.get("OptionalData", ""),
                    f"(https://officer.thaipoliceonline.go.th/pct-in/officer/task-admin-view/{case_item.get('InstId')}#task-admin)",
                    ", ".join([itm.get("CASE_NO") for itm in case_item.get("related_cases", [])]),
                )
                for case_item in filtered_cases
            ]
            create_excel_file(filtered_cases_headers, filtered_cases_body, "all_fetched_cases")

            print(f"================================\nINFO: picked {len(filtered_cases)} cases from {limit}\n================================")

            try:
                user_idx = ask_process(filtered_cases)
                if user_idx != 0:
                    user_idx -= 1
                    selected_case = filtered_cases[user_idx]
                    print(f"You selected: {selected_case.get('TrackingCode')} with {len(selected_case.get('related_cases', []))} related cases.")

                    process_case_details(selected_case, token)
                    create_case_report(selected_case)

                    generate_daily_report(selected_case)
                    generate_sender_report(selected_case)

                    print(f"INFO: xlsx exported {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                print("Goodbye! with exception", e)

        else:
            inst_id = case_id
            selected_case = {"InstId": case_id}
            case_detail = get_case_detail_by_inst_id(token, inst_id)
            selected_case["detail"] = case_detail[0] if case_detail else {}
            selected_case["TrackingCode"] = selected_case.get("detail", {}).get("TRACKING_CODE")

            data_id = selected_case["detail"].get("DATA_ID", 0)
            related_cases = get_related_cases_by_data_id(token, data_id) if data_id else []
            selected_case["related_cases"] = related_cases

            process_case_details(selected_case, token)
            create_case_report(selected_case)

            generate_daily_report(selected_case)
            generate_sender_report(selected_case)

            print(f"INFO: xlsx exported {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
