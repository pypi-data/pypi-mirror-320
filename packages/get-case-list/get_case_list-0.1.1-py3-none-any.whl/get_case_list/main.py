import argparse
import datetime
import getpass
import json

import tqdm

from get_case_list.funcs.auth import login
from get_case_list.funcs.apitools import get_bank_account_by_case_id, get_case_detail_by_case_id, get_case_detail_by_inst_id, get_cases_from_api, get_related_cases_by_data_id
from get_case_list.funcs.prompt import ask_process
from get_case_list.funcs.exceltools import create_excel_file


def main():
    parser = argparse.ArgumentParser(description="Get data from API")
    parser.add_argument("-u", "--username", required=True, help="USERNAME")
    parser.add_argument("-p", "--password", type=str, help="PASSWORD")
    parser.add_argument("-s", "--start_date", type=str, help="2025-01-01", default=datetime.datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("-e", "--end_date", type=str, help="2025-01-01", default=datetime.datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("-l", "--limit", type=str, help="Number of records to fetch", default=5)
    args = parser.parse_args()

    username = args.username
    password = args.password or getpass.getpass("Enter password: ")
    start_date = args.start_date
    end_date = args.end_date
    limit = args.limit

    token = login(username, password)

    if token:
        print(f"INFO: start process with {username} ({start_date} - {end_date}) limit={limit}")
        cases = get_cases_from_api(token, start_date, end_date, limit)

        for case_itm in tqdm.tqdm(cases, desc="Fetching case detail"):
            inst_id = case_itm.get("InstId", None)
            case_detail = get_case_detail_by_inst_id(token, inst_id) if inst_id is not None else []
            if case_detail is not None and case_detail != []:
                case_itm["detail"] = case_detail[0]

        for case_itm in tqdm.tqdm(cases, desc="Fetching related cases"):
            data_id = case_itm.get("detail").get("DATA_ID", 0)
            if data_id != 0:
                related_cases = get_related_cases_by_data_id(token, data_id) if data_id is not None else []
                case_itm["related_cases"] = related_cases if related_cases is not None else []

        filtered_cases = [case for case in cases if len(case.get("related_cases", [])) != 0]
        print("================================")
        print(f"INFO: picked {len(filtered_cases)} cases from {limit}")
        print("================================")

        try:
            user_idx = ask_process(filtered_cases)
            if user_idx != 0:
                user_idx -= 1
                selected_case = filtered_cases[user_idx]
                print(f"You selected: {selected_case.get("TrackingCode")} with {len(selected_case.get("related_cases", []))} related cases.")

                idx_related_case = 0
                for case in tqdm.tqdm(selected_case.get("related_cases", []), "Fetching related case with information"):
                    case_id = case.get("CASE_ID", 0)
                    if case_id != 0:
                        case_detail = get_case_detail_by_case_id(token, case_id)
                        selected_case["related_cases"][idx_related_case] = {**case, **case_detail}
                    idx_related_case += 1

                selected_case["bank_accounts"] = get_bank_account_by_case_id(token, selected_case.get("detail").get("DATA_ID", 0))

                case_informations_headers = ("เลขคดี", "จำนวนเคสที่เกี่ยวข้อง", "รายละเอียด", "Case ids ที่เกี่ยวข้อง")
                case_informations_body = [(selected_case.get("TrackingCode", ""), len(selected_case.get("related_cases", [])), selected_case.get("OptionalData", ""), ", ".join([itm.get("CASE_NO") for itm in selected_case.get("related_cases", [])]))]  # Assuming 'CaseIDs' is a list
                create_excel_file(case_informations_headers, case_informations_body, "selected_case")

                related_cases_headers = ("เลขรับแจ้งความ", "ประเภท", "หน่วยงานที่รับผิดชอบ", "สถานะ", "มูลค่าความเสียหาย", "รายละเอียด")
                related_cases_body = [(itm.get("CASE_NO", ""), itm.get("CASE_TYPE_ABBR", ""), itm.get("ORG_NAME", ""), itm.get("COUNT_RATE", ""), itm.get("DAMAGE_VALUE", ""), itm.get("CASE_BEHAVIOR", "")) for itm in selected_case.get("related_cases", [])]
                create_excel_file(related_cases_headers, related_cases_body, "related_cases")

                bank_account_headers = ["เลขบัญชี", "ชื่อบัญชี", "ธนาคาร"]
                bank_account_body = [(itm.get("BANK_ACCOUNT", ""), itm.get("BANK_ACCOUNT_NAME", ""), itm.get("BANK_NAME", "")) for itm in selected_case.get("bank_accounts", [])]
                create_excel_file(bank_account_headers, bank_account_body, "bank_account")
                print(f"INFO: xlsx exported {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
        except Exception as e:
            print("Goodbye!")


if __name__ == "__main__":
    main()
