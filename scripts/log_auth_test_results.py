import openpyxl
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

# 1. Update Automation Test Cases
auto_path = "docs/Verity_Automation_Test_Cases.xlsx"
wb_auto = openpyxl.load_workbook(auto_path)
ws_auto = wb_auto["Auth"]

test_cases_auto = [
    (
        "AUT-AUTH-001", "TC-AUTH-001", "Auth", "Password Security", "Bcrypt password hashing & verification",
        "Unit", "Pytest", "None", 'Password="SuperSecretPassword123!"',
        "Hash password and verify valid and invalid match", "Hash differs from plaintext; verifies correctly",
        "assert hashed != password; verify_password returns True for match, False for mismatch",
        "backend/tests/test_auth.py::test_password_hashing", "Passed", "", "Local / Epic-1", today, "Verified locally"
    ),
    (
        "AUT-AUTH-002", "TC-AUTH-002", "Auth", "Token Management", "JWT access token creation & payload decoding",
        "Unit", "Pytest", "None", 'user_id=42',
        "Create token and decode subject", "Subject matches user_id and token signature is valid",
        'assert payload["sub"] == "42"',
        "backend/tests/test_auth.py::test_token_encoding_decoding", "Passed", "", "Local / Epic-1", today, "Verified locally"
    ),
    (
        "AUT-AUTH-003", "TC-AUTH-003", "Auth", "Registration", "Successful candidate registration",
        "API", "Pytest / TestClient", "Clean DB session", 'email="candidate1@example.com", password="StrongPassword123"',
        "POST /api/v1/auth/register", "User created with 201 Created and password hash not returned",
        'assert status_code == 201; "hashed_password" not in data',
        "backend/tests/test_auth.py::test_register_user_success", "Passed", "", "Local / Epic-1", today, "Verified locally"
    ),
    (
        "AUT-AUTH-004", "TC-AUTH-004", "Auth", "Registration", "Duplicate email registration conflict",
        "API / Negative", "Pytest / TestClient", "User exists in DB", 'email="duplicate@example.com"',
        "POST /api/v1/auth/register twice with same email", "Second request returns 409 Conflict",
        'assert status_code == 409; "already exists" in detail',
        "backend/tests/test_auth.py::test_register_duplicate_email", "Passed", "", "Local / Epic-1", today, "Verified locally"
    ),
    (
        "AUT-AUTH-005", "TC-AUTH-005", "Auth", "Registration", "Invalid email format rejection",
        "API / Negative", "Pytest / TestClient", "None", 'email="not-an-email"',
        "POST /api/v1/auth/register with malformed email", "Request rejected with 422 Unprocessable Entity",
        "assert status_code == 422",
        "backend/tests/test_auth.py::test_register_invalid_email", "Passed", "", "Local / Epic-1", today, "Verified locally"
    ),
    (
        "AUT-AUTH-006", "TC-AUTH-006", "Auth", "Registration", "Enforce minimum password length",
        "API / Negative", "Pytest / TestClient", "None", 'password="short"',
        "POST /api/v1/auth/register with <8 char password", "Request rejected with 422 Unprocessable Entity",
        "assert status_code == 422",
        "backend/tests/test_auth.py::test_register_short_password", "Passed", "", "Local / Epic-1", today, "Verified locally"
    ),
    (
        "AUT-AUTH-007", "TC-AUTH-007", "Auth", "Authentication", "Successful candidate login and JWT issuance",
        "API", "Pytest / TestClient", "Registered user in DB", 'email="login_user@example.com", password="ValidPassword999"',
        "POST /api/v1/auth/login with valid credentials", "Returns 200 OK with bearer token",
        'assert status_code == 200; "access_token" in data',
        "backend/tests/test_auth.py::test_login_success", "Passed", "", "Local / Epic-1", today, "Verified locally"
    ),
    (
        "AUT-AUTH-008", "TC-AUTH-008", "Auth", "Authentication", "Reject invalid password with 401 Unauthorized",
        "API / Negative", "Pytest / TestClient", "Registered user in DB", 'email="user_bad_pass@example.com", password="WrongPassword!"',
        "POST /api/v1/auth/login with incorrect password", "Returns 401 Unauthorized",
        'assert status_code == 401; "incorrect email or password" in detail',
        "backend/tests/test_auth.py::test_login_invalid_credentials", "Passed", "", "Local / Epic-1", today, "Verified locally"
    ),
    (
        "AUT-AUTH-009", "TC-AUTH-009", "Auth", "User Profile", "Read current user profile via /me",
        "API", "Pytest / TestClient", "Authenticated user with valid token", 'Bearer <token>',
        "GET /api/v1/auth/me with Authorization header", "Returns 200 OK and current user profile details",
        'assert status_code == 200; data["email"] == "me_user@example.com"',
        "backend/tests/test_auth.py::test_read_current_user_me", "Passed", "", "Local / Epic-1", today, "Verified locally"
    ),
    (
        "AUT-AUTH-010", "TC-AUTH-010", "Auth", "Security / RBAC", "Reject unauthenticated request to /me",
        "Security", "Pytest / TestClient", "No authorization header", "None",
        "GET /api/v1/auth/me without header", "Returns 401 Unauthorized",
        "assert status_code == 401",
        "backend/tests/test_auth.py::test_read_current_user_unauthorized", "Passed", "", "Local / Epic-1", today, "Verified locally"
    ),
    (
        "AUT-AUTH-011", "TC-AUTH-011", "Auth", "Security / RBAC", "Reject forged JWT bearer token",
        "Security", "Pytest / TestClient", "None", 'Bearer "forged.token.value"',
        "GET /api/v1/auth/me with invalid token", "Returns 401 Unauthorized",
        "assert status_code == 401",
        "backend/tests/test_auth.py::test_read_current_user_invalid_token", "Passed", "", "Local / Epic-1", today, "Verified locally"
    ),
    (
        "AUT-AUTH-012", "TC-AUTH-012", "Auth", "User Isolation", "Cross-user data isolation enforcement",
        "Security", "Pytest / TestClient", "Two distinct registered users in DB", "User1 and User2 credentials",
        "Request /me with User1 token", "Returned profile strictly matches User1; User2 data remains inaccessible",
        'assert me_res.json()["email"] == "user1@example.com" and != "user2@example.com"',
        "backend/tests/test_auth.py::test_user_isolation", "Passed", "", "Local / Epic-1", today, "Verified locally"
    ),
]

for row in test_cases_auto:
    ws_auto.append(row)

# Update 00_Index in Auto workbook
idx_ws_auto = wb_auto["00_Index"]
for row in idx_ws_auto.iter_rows(min_row=2):
    if row[0].value == "Auth":
        row[2].value = len(test_cases_auto)
        row[3].value = today
        row[4].value = len(test_cases_auto)
        row[5].value = 0
        row[6].value = 0
        row[7].value = "12 automated tests passed (Unit, API, Security)"
        break

wb_auto.save(auto_path)

# 2. Update Manual Test Cases
man_path = "docs/Verity_Manual_Test_Cases.xlsx"
wb_man = openpyxl.load_workbook(man_path)
ws_man = wb_man["Auth"]

test_cases_man = [
    (
        "TC-AUTH-001", "Auth", "Registration", "Register new account via UI",
        "Browser on Auth page", 'Email: user@local.test, Pass: Secret1234',
        "1. Enter email and password. 2. Click Register Account.",
        "Account created and user logged in, navigating to Workspace",
        "High", "P1", "Functional", "Local Dev",
        "Account registered successfully; session stored in localStorage", "Passed", "", "QA Engineer", today, "", "Verified in browser"
    ),
    (
        "TC-AUTH-002", "Auth", "Authentication", "Login with valid credentials",
        "User registered in DB", 'Email: user@local.test, Pass: Secret1234',
        "1. Enter credentials. 2. Click Sign In.",
        "JWT token stored and user name displayed in top nav",
        "High", "P1", "Functional", "Local Dev",
        "User authenticated, token persisted, navbar shows user state", "Passed", "", "QA Engineer", today, "", "Verified in browser"
    ),
    (
        "TC-AUTH-003", "Auth", "Authentication", "Sign out flow",
        "User currently logged in", "None",
        "1. Go to Auth view. 2. Click Sign Out.",
        "JWT token cleared from localStorage and guest view restored",
        "Medium", "P2", "Functional", "Local Dev",
        "Token removed, user status returns to Guest Session", "Passed", "", "QA Engineer", today, "", "Verified in browser"
    ),
]

for row in test_cases_man:
    ws_man.append(row)

# Update 00_Index in Manual workbook
idx_ws_man = wb_man["00_Index"]
for row in idx_ws_man.iter_rows(min_row=2):
    if row[0].value == "Auth":
        row[2].value = len(test_cases_man)
        row[3].value = today
        row[4].value = len(test_cases_man)
        row[5].value = 0
        row[6].value = 0
        row[7].value = "3 manual functional/UI tests passed"
        break

wb_man.save(man_path)
print("Updated test workbooks successfully!")
