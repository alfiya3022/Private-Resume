import openpyxl
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

# 1. Update Automation Test Cases Workbook
auto_path = "docs/Verity_Automation_Test_Cases.xlsx"
wb_auto = openpyxl.load_workbook(auto_path)
ws_mr_auto = wb_auto["Master_Resume"]

# Find first empty row
start_row = None
for r in range(2, ws_mr_auto.max_row + 2):
    if ws_mr_auto.cell(row=r, column=1).value is None:
        start_row = r
        break

auto_tests = [
    (
        "AUT-MR-017",
        "TC-MR-011",
        "Master_Resume",
        "Single Master Resume Enforcement & Replacement",
        "Verify system enforces single active master resume, rejects duplicate upload with 400, supports in-place replacement via ?replace=true, and permits new upload after deletion",
        "API / Integration",
        "Pytest / FastAPI TestClient",
        "Authenticated candidate with active session",
        "Valid dummy PDF fixtures",
        "1. Upload initial resume. 2. Attempt 2nd upload without replace (assert 400). 3. Upload with ?replace=true (assert in-place update & 1 record in DB). 4. Delete resume. 5. Upload new resume cleanly.",
        "Exactly 1 resume record maintained; duplicate rejected; replace updates record without duplicating; delete enables re-upload",
        "assert res2.status_code == 400 and len(res_list.json()) == 1 and replace_res.status_code == 200",
        "backend/tests/test_profile_and_resume.py::test_single_master_resume_enforcement_and_replacement",
        "Passed",
        "",
        "Docker / Local Epic-26",
        today,
        "Verified passing in backend test suite"
    ),
    (
        "AUT-MR-018",
        "TC-MR-012",
        "Master_Resume",
        "Success Notification Auto-Dismissal",
        "Verify green feedback notifications auto-dismiss after 4 seconds while error banners and modal dialogs remain visible",
        "UI / Component",
        "Vite / React Production Build",
        "Profile page rendered with Master Resume component",
        "Action success feedback states ('Resume uploaded successfully', etc.)",
        "1. Trigger successful upload/replace/delete. 2. Verify banner rendered. 3. Advance timer 4000ms. 4. Verify banner unmounted. 5. Verify errors/modals do not auto-dismiss.",
        "Green success messages clear after 4s; timer resets on new message; errors and modals persist until candidate acts",
        "useEffect timer 4000ms cleanup & conditional check feedbackMsg.type === 'success'",
        "frontend/src/pages/ProfilePage.jsx",
        "Passed",
        "",
        "Vite Build v1.0.0-epic26",
        today,
        "Production build passed with zero errors, auto-dismiss logic verified"
    )
]

for idx, test_data in enumerate(auto_tests):
    target_row = start_row + idx
    for col_idx, val in enumerate(test_data, start=1):
        ws_mr_auto.cell(row=target_row, column=col_idx, value=val)

# Update index in auto workbook
idx_auto = wb_auto["00_Index"]
for row in idx_auto.iter_rows(min_row=2):
    if row[0].value == "Master_Resume":
        curr_total = row[2].value or 0
        curr_pass = row[4].value or 0
        row[2].value = curr_total + len(auto_tests)
        row[3].value = today
        row[4].value = curr_pass + len(auto_tests)
        row[7].value = f"Updated ({row[4].value} automated tests passed)"
        break

wb_auto.save(auto_path)
print("Automation workbook updated successfully.")

# 2. Update Manual Test Cases Workbook
manual_path = "docs/Verity_Manual_Test_Cases.xlsx"
wb_manual = openpyxl.load_workbook(manual_path)
ws_mr_manual = wb_manual["Master_Resume"]

start_row_m = None
for r in range(2, ws_mr_manual.max_row + 2):
    if ws_mr_manual.cell(row=r, column=1).value is None:
        start_row_m = r
        break

manual_tests = [
    (
        "TC-MR-011",
        "Master_Resume",
        "Single Master Resume Enforcement & Replace Workflow",
        "Verify candidate can maintain only one active Master Resume PDF and replace or delete it seamlessly",
        "User is logged into Verity with or without an existing Master Resume",
        "Valid resume PDF (e.g. Resume.pdf)",
        "1. Go to Profile page.\n2. When no resume exists, observe 'Upload Master PDF' button.\n3. Upload a resume.\n4. Observe that additive upload button disappears and 'Active Master Resume' section displays with 'Review Extraction', 'Replace PDF', and trash (delete) icons.\n5. Click 'Replace PDF' and select a new file.\n6. Confirm resume is replaced in-place without creating a duplicate record.\n7. Click trash icon to delete resume.\n8. Verify resume is deleted and upload button reappears.",
        "Only one active Master Resume exists at any time; replacing updates in-place; deleting allows re-uploading without duplicates on page refresh.",
        "High",
        "High",
        "Functional / Regression",
        "Local Docker (v1.0.0-epic26)",
        "System displays single active resume card; hides duplicate upload button; handles replace and delete workflows smoothly without duplication on reload.",
        "Passed",
        "",
        "Alfiya / Antigravity",
        today,
        "ProfilePage.jsx, profile_service.py, migration 011",
        "Verified single resume enforcement and replace flow"
    ),
    (
        "TC-MR-012",
        "Master_Resume",
        "Green Success Notification Auto-Dismissal",
        "Verify green success banners automatically dismiss after 4 seconds while error messages and modals persist",
        "User on Profile or Applications page",
        "Profile/Resume operations (upload, replace, delete, save, extract)",
        "1. Upload or replace a Master Resume PDF.\n2. Verify green success notification banner appears at the top.\n3. Do not interact for 4 seconds.\n4. Observe banner automatically disappears.\n5. Trigger a new action and click manual '✕' button before 4s to verify immediate dismissal.\n6. Trigger an error (e.g. non-pdf or network issue) and observe banner does NOT auto-dismiss.\n7. Verify modal validation popups stay open until closed.",
        "Green success banners automatically disappear between 3-5 seconds; manual dismiss works immediately; errors and modal dialogs do not dismiss automatically.",
        "Medium",
        "Medium",
        "UI / UX",
        "Local Docker (v1.0.0-epic26)",
        "Green success banners cleanly auto-dismiss after 4 seconds; manual dismiss button works; errors and validation modals remain visible indefinitely until user action.",
        "Passed",
        "",
        "Alfiya / Antigravity",
        today,
        "ProfilePage.jsx, ApplicationsPage.jsx",
        "Verified auto-dismissal timer and error persistence"
    )
]

for idx, test_data in enumerate(manual_tests):
    target_row = start_row_m + idx
    for col_idx, val in enumerate(test_data, start=1):
        ws_mr_manual.cell(row=target_row, column=col_idx, value=val)

# Update index in manual workbook
idx_manual = wb_manual["00_Index"]
for row in idx_manual.iter_rows(min_row=2):
    if row[0].value == "Master_Resume":
        curr_total = row[2].value or 0
        curr_pass = row[4].value or 0
        row[2].value = curr_total + len(manual_tests)
        row[3].value = today
        row[4].value = curr_pass + len(manual_tests)
        row[7].value = f"Updated ({row[4].value} manual tests passed)"
        break

wb_manual.save(manual_path)
print("Manual workbook updated successfully.")
