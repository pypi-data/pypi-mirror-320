def ask_process(filtered_cases):
    print("================================")
    idx = 1
    for case_itm in filtered_cases:
        print(f"{idx}. {case_itm.get("TrackingCode")} - {len(case_itm.get("related_cases", []))} related cases (https://officer.thaipoliceonline.go.th/pct-in/officer/task-admin-view/{case_itm.get("InstId")}#task-admin)")
        idx += 1
    print("================================")
    user_idx = int(input("Enter the number of the case you want to select: "))
    result = user_idx if 1 <= user_idx <= len(filtered_cases) else 0
    return result
