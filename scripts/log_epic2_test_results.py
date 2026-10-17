import openpyxl
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

# 1. Update Automation Test Cases
auto_path = "docs/PrivateResume_Automation_Test_Cases.xlsx"
wb_auto = openpyxl.load_workbook(auto_path)

# Log into Master_Resume
ws_mr_auto = wb_auto["Master_Resume"]
mr_tests = [
    (
        "AUT-MR-001", "TC-MR-001", "Master_Resume", "PDF Parsing", "PyMuPDF text extraction & section segmentation",
        "Unit", "Pytest / PyMuPDF", "Valid PDF bytes in-memory", "Synthetic Alice Candidate PDF",
        "Extract text and call segment_sections", "Text contains all expected sections",
        "assert 'ALICE CANDIDATE' in text and 'skills' in sections",
        "backend/tests/test_profile_and_resume.py::test_pdf_service_text_and_sections",
        "Passed", "", "Local / Epic-2", today, "Verified locally"
    ),
    (
        "AUT-MR-002", "TC-MR-002", "Master_Resume", "Skill Detection", "Deterministic tech skill extraction",
        "Unit", "Pytest / Regex", "None", "Sample text with Python, React, PostgreSQL",
        "Run detect_skills_deterministically", "Matches known skills with canonical casing; rejects unmentioned skills",
        "assert 'Python' in skills and 'Rust' not in skills",
        "backend/tests/test_profile_and_resume.py::test_pdf_service_deterministic_skill_detection",
        "Passed", "", "Local / Epic-2", today, "Verified locally"
    ),
    (
        "AUT-MR-003", "TC-MR-003", "Master_Resume", "PDF Upload", "Upload master PDF, parse text and auto-seed skills",
        "API", "Pytest / TestClient", "Authenticated candidate", "Synthetic PDF multipart upload",
        "POST /api/v1/resumes", "Returns 201 Created, parses text, auto-populates skills in profile",
        "assert response.status_code == 201 and 'Python' in data['extracted_skills']",
        "backend/tests/test_profile_and_resume.py::test_upload_master_resume_pdf",
        "Passed", "", "Local / Epic-2", today, "Verified locally"
    ),
    (
        "AUT-MR-004", "TC-MR-004", "Master_Resume", "Negative Upload", "Reject non-PDF file upload with 400",
        "API / Negative", "Pytest / TestClient", "Authenticated candidate", "malicious.exe binary stream",
        "POST /api/v1/resumes with .exe", "Returns 400 Bad Request with descriptive message",
        "assert response.status_code == 400 and 'only pdf files' in detail",
        "backend/tests/test_profile_and_resume.py::test_upload_non_pdf_fails",
        "Passed", "", "Local / Epic-2", today, "Verified locally"
    ),
    (
        "AUT-MR-005", "TC-MR-005", "Master_Resume", "Negative Upload", "Reject empty 0-byte upload with 400",
        "API / Negative", "Pytest / TestClient", "Authenticated candidate", "0-byte PDF stream",
        "POST /api/v1/resumes with empty body", "Returns 400 Bad Request",
        "assert response.status_code == 400 and 'file is empty' in detail",
        "backend/tests/test_profile_and_resume.py::test_upload_empty_pdf_fails",
        "Passed", "", "Local / Epic-2", today, "Verified locally"
    ),
]

for row in mr_tests:
    ws_mr_auto.append(row)

# Log into Profile_Personal
ws_prof_auto = wb_auto["Profile_Personal"]
prof_tests = [
    (
        "AUT-PROF-001", "TC-PROF-001", "Profile_Personal", "Profile CRUD", "Get and update profile metadata",
        "API", "Pytest / TestClient", "Authenticated candidate", "ProfileUpdate payload",
        "GET /api/v1/profile, then PUT /api/v1/profile", "Profile auto-initialized, updated with 200 OK",
        "assert updated['headline'] == 'Senior Full-Stack Engineer'",
        "backend/tests/test_profile_and_resume.py::test_get_and_update_profile",
        "Passed", "", "Local / Epic-2", today, "Verified locally"
    ),
    (
        "AUT-PROF-002", "TC-PROF-002", "Profile_Personal", "Sub-items CRUD", "CRUD for skills, projects, and experiences",
        "API", "Pytest / TestClient", "Authenticated candidate", "Skill, project, experience payloads",
        "POST and DELETE on /profile/skills, /profile/projects, /profile/experiences", "Created with 201, deleted with 204",
        "assert status_code == 201 and delete status == 204",
        "backend/tests/test_profile_and_resume.py::test_profile_subitems_crud",
        "Passed", "", "Local / Epic-2", today, "Verified locally"
    ),
    (
        "AUT-PROF-003", "TC-PROF-003", "Profile_Personal", "User Isolation", "Cross-user profile and resume isolation",
        "Security", "Pytest / TestClient", "Two distinct registered users", "User 1 and User 2 tokens",
        "User 2 attempts to delete User 1 skill and resume", "Rejected with 404 Not Found; User 2 resume list is empty",
        "assert del_skill.status_code == 404 and del_resume.status_code == 404",
        "backend/tests/test_profile_and_resume.py::test_profile_and_resume_user_isolation",
        "Passed", "", "Local / Epic-2", today, "Verified locally"
    ),
]

for row in prof_tests:
    ws_prof_auto.append(row)

# Update Index in Auto workbook
idx_ws_auto = wb_auto["00_Index"]
for row in idx_ws_auto.iter_rows(min_row=2):
    if row[0].value == "Master_Resume":
        row[2].value = len(mr_tests)
        row[3].value = today
        row[4].value = len(mr_tests)
        row[5].value = 0
        row[6].value = 0
        row[7].value = "5 automated tests passed (Unit, API, Security)"
    elif row[0].value == "Profile_Personal":
        row[2].value = len(prof_tests)
        row[3].value = today
        row[4].value = len(prof_tests)
        row[5].value = 0
        row[6].value = 0
        row[7].value = "3 automated tests passed (API, CRUD, Isolation)"

wb_auto.save(auto_path)

# 2. Update Manual Test Cases
man_path = "docs/PrivateResume_Manual_Test_Cases.xlsx"
wb_man = openpyxl.load_workbook(man_path)
ws_mr_man = wb_man["Master_Resume"]

mr_man_tests = [
    (
        "TC-MR-001", "Master_Resume", "PDF Upload", "Upload PDF resume from browser",
        "Candidate logged in", "Sample candidate PDF file",
        "1. Click 'Upload Master PDF'. 2. Select PDF file. 3. Confirm upload.",
        "File uploaded, text parsed via PyMuPDF, skills populated in Skills tab",
        "High", "P1", "Functional", "Local Dev",
        "File uploaded, feedback message displayed, skills visible in Skills list", "Passed", "", "QA Engineer", today, "", "Verified in browser"
    ),
    (
        "TC-MR-002", "Master_Resume", "File Validation", "Upload invalid file format (non-PDF)",
        "Candidate logged in", "Sample .png or .txt file",
        "1. Select non-PDF file in upload dialog.",
        "Upload blocked or rejected with clear user error message",
        "Medium", "P2", "Validation", "Local Dev",
        "File input restricts to .pdf, backend returns 400 Bad Request error", "Passed", "", "QA Engineer", today, "", "Verified in browser"
    ),
]

for row in mr_man_tests:
    ws_mr_man.append(row)

# Update Index in Manual workbook
idx_ws_man = wb_man["00_Index"]
for row in idx_ws_man.iter_rows(min_row=2):
    if row[0].value == "Master_Resume":
        row[2].value = len(mr_man_tests)
        row[3].value = today
        row[4].value = len(mr_man_tests)
        row[5].value = 0
        row[6].value = 0
        row[7].value = "2 manual test cases executed and passed"
        break

wb_man.save(man_path)
print("Updated Epic 2 test cases successfully!")
