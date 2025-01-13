import requests


def get_cases_from_api(token, start_date, end_date, limit, keyword):
    cases = []
    try:
        headers = {"Authorization": f"Bearer {token}"}
        if keyword == "":
            result = requests.get(
                f"https://officer.thaipoliceonline.go.th/api/e-form/v1.0/BpmProcInst/workflow/task-list-new?RequireTotalCount=true&RoleCode=ROOT&Offset=0&Length={limit}&SortSelector=TrackingCode&SortDesc=true&StartDate={start_date}&EndDate={end_date}&CategoryId=1&Casetype=&IsCheck=&RequireStuckCase=false",
                headers=headers,
            )
        else:
            result = requests.get(
                f"https://officer.thaipoliceonline.go.th/api/e-form/v1.0/BpmProcInst/workflow/task-list-new?CposText={keyword}&RequireTotalCount=true&RoleCode=ROOT&Offset=0&Length={limit}&SortSelector=TrackingCode&SortDesc=true&StartDate={start_date}&EndDate={end_date}&CategoryId=1&Casetype=&IsCheck=&RequireStuckCase=false",
                headers=headers,
            )
        if result.status_code == 200:
            result = result.json()
            cases = result.get("Value", {}).get("Data", [])
    except Exception as e:
        print("Error: when try to get case")
    return cases


def get_case_detail_by_inst_id(token, id):
    case_detail = []
    try:
        headers = {"Authorization": f"Bearer {token}"}
        result = requests.get(f"https://officer.thaipoliceonline.go.th/api/e-form/v1.0/BpmProcInstLog?instId={id}&excludeSystemCreate=true", headers=headers)
        if result.status_code == 200:
            result = result.json()
            case_detail = result.get("Value", [])
    except Exception as e:
        print("Error: when try to get case")
    return case_detail


def get_related_cases_by_data_id(token, id):
    cases = []
    try:
        headers = {"Authorization": f"Bearer {token}"}
        result = requests.post(f"https://officer.thaipoliceonline.go.th/api/ccib/v1.0/CmsOnlineCaseInfo/{id}/relation", json={"Offset": 0, "Length": 10000}, headers=headers)
        if result.status_code == 200:
            result = result.json()
            cases = result.get("Value", {}).get("Data", [])
    except Exception as e:
        print("Error: when try to get case")
    return cases


def get_case_detail_by_case_id(token, id):
    case_detail = []
    try:
        headers = {"Authorization": f"Bearer {token}"}
        result = requests.get(f"https://officer.thaipoliceonline.go.th/api/ccib/v1.0/CmsOnlineCaseInfo/getbycaseid/{id}", headers=headers)
        if result.status_code == 200:
            result = result.json()
            case_detail = result.get("Value", {})
    except Exception as e:
        print("Error: when try to get case")
    return case_detail


def get_bank_account_by_case_id(token, id):
    bank_account = []
    try:
        headers = {"Authorization": f"Bearer {token}"}
        result = requests.get(f"https://officer.thaipoliceonline.go.th/api/ccib/v1.0/CmsOnlineCaseInfo/casemoney/{id}", headers=headers)
        if result.status_code == 200:
            result = result.json()
            bank_account = result.get("Value", {})
    except Exception as e:
        print("Error: when try to get case")
    return bank_account
