import time
import requests
import json
import statistics
import subprocess

API_URL = "http://localhost:8000/api/v1"

def get_auth_token():
    res = subprocess.check_output([
        "docker", "exec", "Verity_backend", "python", "-c",
        "from app.core.security import create_access_token; print(create_access_token('1'))"
    ]).decode().strip()
    return res

def get_container_rss():
    out = subprocess.check_output([
        "docker", "exec", "Verity_backend", "python", "-c",
        "import psutil; procs = [p.memory_info().rss for p in psutil.process_iter() if 'python' in p.name() or 'uvicorn' in p.name()]; print(round(max(procs) / 1024 / 1024, 2) if procs else 0)"
    ]).decode().strip()
    return float(out)

def run_single_upload(pdf_path, token, label="run"):
    rss_before = get_container_rss()
    
    t_post_start = time.perf_counter()
    with open(pdf_path, "rb") as f:
        resp = requests.post(
            f"{API_URL}/resumes?replace=true",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": (f"{label}_resume.pdf", f, "application/pdf")}
        )
    t_post_end = time.perf_counter()
    post_duration = t_post_end - t_post_start
    
    assert resp.status_code == 202, f"POST failed: {resp.status_code} - {resp.text}"
    data = resp.json()
    resume_id = data["resume_id"]
    
    # Poll until complete
    poll_start = time.perf_counter()
    peak_rss = rss_before
    status = "queued"
    stage_transitions = []
    
    while True:
        curr_rss = get_container_rss()
        if curr_rss > peak_rss:
            peak_rss = curr_rss
            
        st_resp = requests.get(
            f"{API_URL}/resumes/{resume_id}/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        st_data = st_resp.json()
        curr_status = st_data.get("parse_status")
        curr_stage = st_data.get("parse_stage")
        stage_transitions.append((round(time.perf_counter() - t_post_start, 3), curr_status, curr_stage))
        
        if curr_status in ("complete", "failed"):
            status = curr_status
            break
        time.sleep(0.05)
        if time.perf_counter() - poll_start > 30:
            status = "timeout"
            break
            
    total_time = time.perf_counter() - t_post_start
    rss_after = get_container_rss()
    
    # Get parsed details
    detail_resp = requests.get(
        f"{API_URL}/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    detail_data = detail_resp.json()
    
    return {
        "label": label,
        "resume_id": resume_id,
        "status": status,
        "post_duration_seconds": round(post_duration, 4),
        "total_time_seconds": round(total_time, 4),
        "rss_before_mb": rss_before,
        "peak_rss_mb": peak_rss,
        "rss_after_mb": rss_after,
        "stage_transitions": stage_transitions[:10],
        "extracted_skills_count": len(detail_data.get("extracted_data", {}).get("skills", [])),
        "projects_count": len(detail_data.get("extracted_data", {}).get("projects", [])),
        "experience_count": len(detail_data.get("extracted_data", {}).get("experience", []))
    }

if __name__ == "__main__":
    pdf_path = "backend/tests/fixtures/master_resume_reference.pdf"
    token = get_auth_token()
    print("Executing Warm Start 5-Run Sequence...")
    runs = []
    for i in range(1, 6):
        res = run_single_upload(pdf_path, token, f"warm_{i}")
        runs.append(res)
        print(f"Run {i}: total={res['total_time_seconds']}s, post_202={res['post_duration_seconds']}s, status={res['status']}")
    
    totals = [r["total_time_seconds"] for r in runs]
    posts = [r["post_duration_seconds"] for r in runs]
    median_total = statistics.median(totals)
    median_post = statistics.median(posts)
    
    summary = {
        "runs": runs,
        "median_total_seconds": round(median_total, 4),
        "median_post_202_seconds": round(median_post, 4),
        "min_total_seconds": min(totals),
        "max_total_seconds": max(totals)
    }
    print("--- SUMMARY ---")
    print(json.dumps(summary, indent=2))

