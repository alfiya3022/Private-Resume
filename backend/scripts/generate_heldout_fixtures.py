import os
import json
import fitz  # PyMuPDF

HELDOUT_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "heldout")
os.makedirs(HELDOUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# Document 1: Two-column layout (Sidebar on left, Main on right)
# -------------------------------------------------------------
def create_doc1():
    doc = fitz.open()
    page = doc.new_page(width=612, height=792) # Standard Letter
    
    # Left Column (Sidebar, x: 40 to 200)
    # Header in sidebar
    page.insert_text((40, 50), "Devon Vance", fontsize=18, fontname="helv", color=(0.1, 0.1, 0.1))
    page.insert_text((40, 70), "devon.vance@example.com", fontsize=9, fontname="helv")
    page.insert_text((40, 85), "+1 (512) 555-0199", fontsize=9, fontname="helv")
    page.insert_text((40, 100), "Austin, TX", fontsize=9, fontname="helv")
    page.insert_text((40, 115), "linkedin.com/in/devonvance", fontsize=9, fontname="helv")
    page.insert_text((40, 130), "github.com/devonvance", fontsize=9, fontname="helv")
    
    # Skills in sidebar
    page.insert_text((40, 160), "SKILLS", fontsize=12, fontname="helv", color=(0.2, 0.2, 0.2))
    page.draw_line((40, 165), (190, 165), color=(0.7, 0.7, 0.7), width=1)
    
    skills = [
        "Python", "Go", "Docker", "Kubernetes", "PostgreSQL",
        "Redis", "AWS", "Terraform", "Prometheus", "Git"
    ]
    y = 185
    for s in skills:
        page.insert_text((40, y), f"• {s}", fontsize=10, fontname="helv")
        y += 18
        
    # Education in sidebar
    page.insert_text((40, 400), "EDUCATION", fontsize=12, fontname="helv", color=(0.2, 0.2, 0.2))
    page.draw_line((40, 405), (190, 405), color=(0.7, 0.7, 0.7), width=1)
    page.insert_text((40, 425), "B.S. in Computer Science", fontsize=9, fontname="helv")
    page.insert_text((40, 440), "University of Texas at Austin", fontsize=9, fontname="helv")
    page.insert_text((40, 455), "2018 - 2022", fontsize=9, fontname="helv")
    page.insert_text((40, 470), "CGPA: 3.85 / 4.0", fontsize=9, fontname="helv")
    
    # Right Column (Main content, x: 220 to 570)
    page.insert_text((220, 50), "Senior Cloud Infrastructure Engineer", fontsize=12, fontname="helv", color=(0.3, 0.3, 0.3))
    
    # Summary
    page.insert_text((220, 80), "SUMMARY", fontsize=12, fontname="helv", color=(0.2, 0.2, 0.2))
    page.draw_line((220, 85), (570, 85), color=(0.7, 0.7, 0.7), width=1)
    page.insert_textbox(
        fitz.Rect(220, 95, 570, 145),
        "Cloud engineer with 4+ years of experience automating distributed systems and resilient microservices. Proven expertise in container orchestration and declarative infrastructure.",
        fontsize=9.5, fontname="helv"
    )
    
    # Experience
    page.insert_text((220, 160), "WORK EXPERIENCE", fontsize=12, fontname="helv", color=(0.2, 0.2, 0.2))
    page.draw_line((220, 165), (570, 165), color=(0.7, 0.7, 0.7), width=1)
    
    page.insert_text((220, 185), "Site Reliability Engineer | CloudScale Inc", fontsize=10.5, fontname="helv")
    page.insert_text((480, 185), "2022 - Present", fontsize=9.5, fontname="helv")
    exp_bullets = [
        "Architected multi-region Kubernetes clusters supporting 250M daily active requests with 99.99% uptime.",
        "Implemented Terraform modules cutting infrastructure provisioning cycle from 3 days to 15 minutes.",
        "Configured Prometheus monitoring dashboards reducing mean time to detection (MTTD) by 40%."
    ]
    ey = 205
    for b in exp_bullets:
        page.insert_textbox(fitz.Rect(230, ey, 570, ey + 30), f"•  {b}", fontsize=9, fontname="helv")
        ey += 28
        
    # Projects
    page.insert_text((220, 310), "PROJECTS", fontsize=12, fontname="helv", color=(0.2, 0.2, 0.2))
    page.draw_line((220, 315), (570, 315), color=(0.7, 0.7, 0.7), width=1)
    
    page.insert_text((220, 335), "Distributed Log Aggregator | Go, Docker, Redis", fontsize=10.5, fontname="helv")
    page.insert_text((480, 335), "2023 - 2024", fontsize=9.5, fontname="helv")
    proj_bullets = [
        "Built high-throughput log processing pipeline ingesting 50k events/sec using Go worker pools and Redis streams.",
        "Packaged containerized services with minimal alpine Docker images under 15MB."
    ]
    py = 355
    for pb in proj_bullets:
        page.insert_textbox(fitz.Rect(230, py, 570, py + 25), f"•  {pb}", fontsize=9, fontname="helv")
        py += 24
        
    pdf_path = os.path.join(HELDOUT_DIR, "doc1_two_column_sidebar.pdf")
    doc.save(pdf_path)
    doc.close()

    # Handcrafted Expected JSON for Doc 1
    expected1 = {
        "personal_info": {
            "name": "Devon Vance",
            "email": "devon.vance@example.com",
            "phone": "+1 (512) 555-0199",
            "location": "Austin, TX",
            "linkedin_url": "linkedin.com/in/devonvance",
            "github_url": "github.com/devonvance"
        },
        "summary": "Cloud engineer with 4+ years of experience automating distributed systems and resilient microservices. Proven expertise in container orchestration and declarative infrastructure.",
        "expected_skills": ["Python", "Go", "Docker", "Kubernetes", "PostgreSQL", "Redis", "AWS", "Terraform", "Prometheus", "Git"],
        "education": [
            {
                "institution": "University of Texas at Austin",
                "degree": "B.S. in Computer Science",
                "grade": "3.85 / 4.0"
            }
        ],
        "experience": [
            {
                "company": "CloudScale Inc",
                "title": "Site Reliability Engineer",
                "start_date": "2022",
                "end_date": "Present"
            }
        ],
        "projects": [
            {
                "title": "Distributed Log Aggregator",
                "technologies": ["Go", "Docker", "Redis"]
            }
        ]
    }
    with open(os.path.join(HELDOUT_DIR, "doc1.expected.json"), "w", encoding="utf-8") as f:
        json.dump(expected1, f, indent=2)

# -------------------------------------------------------------
# Document 2: Title Case Headings ("Technical Exposure", etc.)
# -------------------------------------------------------------
def create_doc2():
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    
    # Header
    page.insert_text((50, 45), "Maya Lin", fontsize=20, fontname="helv")
    page.insert_text((50, 65), "maya.lin@example.com | (415) 555-8282 | San Francisco, CA | linkedin.com/in/mayalin", fontsize=9, fontname="helv")
    
    # Section 1: Professional Summary
    page.insert_text((50, 95), "Professional Summary", fontsize=13, fontname="helv")
    page.draw_line((50, 100), (560, 100), color=(0.6, 0.6, 0.6), width=1)
    page.insert_textbox(
        fitz.Rect(50, 110, 560, 140),
        "Full-stack software developer with deep expertise in modern React frameworks, TypeScript, and high-performance asynchronous Python APIs.",
        fontsize=9.5, fontname="helv"
    )
    
    # Section 2: Technical Exposure (Title Case)
    page.insert_text((50, 155), "Technical Exposure", fontsize=13, fontname="helv")
    page.draw_line((50, 160), (560, 160), color=(0.6, 0.6, 0.6), width=1)
    page.insert_text((50, 175), "Languages & Frameworks: React, TypeScript, Python, FastAPI, Next.js, Node.js", fontsize=9.5, fontname="helv")
    page.insert_text((50, 192), "Storage & Tools: PostgreSQL, Redis, Docker, Tailwind CSS, Jest, Git", fontsize=9.5, fontname="helv")
    
    # Section 3: Work History (Title Case)
    page.insert_text((50, 220), "Work History", fontsize=13, fontname="helv")
    page.draw_line((50, 225), (560, 225), color=(0.6, 0.6, 0.6), width=1)
    page.insert_text((50, 245), "Full Stack Software Engineer — FinTech Labs", fontsize=10.5, fontname="helv")
    page.insert_text((450, 245), "Mar 2021 – Present", fontsize=9.5, fontname="helv")
    bullets = [
        "Developed financial analytics dashboard in React and Tailwind CSS serving 15,000 corporate clients.",
        "Built real-time transaction ledger endpoints in FastAPI reducing latency from 320ms to 45ms.",
        "Mentored 4 junior engineers on unit testing patterns and TypeScript type safety."
    ]
    by = 265
    for b in bullets:
        page.insert_textbox(fitz.Rect(60, by, 560, by + 22), f"•  {b}", fontsize=9, fontname="helv")
        by += 20
        
    # Section 4: Key Deliverables & Projects (Title Case)
    page.insert_text((50, 345), "Key Deliverables & Projects", fontsize=13, fontname="helv")
    page.draw_line((50, 350), (560, 350), color=(0.6, 0.6, 0.6), width=1)
    page.insert_text((50, 370), "Open Source Task Workflow Engine (TypeScript, React, Node.js)", fontsize=10, fontname="helv")
    page.insert_text((470, 370), "2023", fontsize=9.5, fontname="helv")
    page.insert_textbox(fitz.Rect(60, 385, 560, 415), "•  Engineered drag-and-drop workflow builder with local persistence and zero external tracking.", fontsize=9, fontname="helv")
    
    # Section 5: Academic Background (Title Case)
    page.insert_text((50, 435), "Academic Background", fontsize=13, fontname="helv")
    page.draw_line((50, 440), (560, 440), color=(0.6, 0.6, 0.6), width=1)
    page.insert_text((50, 460), "Bachelor of Science in Software Engineering — San Jose State University", fontsize=10, fontname="helv")
    page.insert_text((470, 460), "2017 – 2021", fontsize=9.5, fontname="helv")
    
    # Section 6: Professional Credentials (Title Case)
    page.insert_text((50, 495), "Professional Credentials", fontsize=13, fontname="helv")
    page.draw_line((50, 500), (560, 500), color=(0.6, 0.6, 0.6), width=1)
    page.insert_text((50, 520), "AWS Certified Solutions Architect — Amazon Web Services (2023)", fontsize=9.5, fontname="helv")
    
    pdf_path = os.path.join(HELDOUT_DIR, "doc2_title_case_headings.pdf")
    doc.save(pdf_path)
    doc.close()

    expected2 = {
        "personal_info": {
            "name": "Maya Lin",
            "email": "maya.lin@example.com",
            "phone": "(415) 555-8282",
            "location": "San Francisco, CA",
            "linkedin_url": "linkedin.com/in/mayalin"
        },
        "summary": "Full-stack software developer with deep expertise in modern React frameworks, TypeScript, and high-performance asynchronous Python APIs.",
        "expected_skills": ["React", "TypeScript", "Python", "FastAPI", "Next.js", "Node.js", "PostgreSQL", "Redis", "Docker", "Tailwind CSS", "Jest", "Git"],
        "experience": [
            {
                "company": "FinTech Labs",
                "title": "Full Stack Software Engineer",
                "start_date": "Mar 2021",
                "end_date": "Present"
            }
        ],
        "projects": [
            {
                "title": "Open Source Task Workflow Engine",
                "technologies": ["TypeScript", "React", "Node.js"]
            }
        ],
        "education": [
            {
                "institution": "San Jose State University",
                "degree": "Bachelor of Science in Software Engineering",
                "end_date": "2021"
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services"
            }
        ]
    }
    with open(os.path.join(HELDOUT_DIR, "doc2.expected.json"), "w", encoding="utf-8") as f:
        json.dump(expected2, f, indent=2)

# -------------------------------------------------------------
# Document 3: Plain-text URLs, left-aligned header (No link annotations)
# -------------------------------------------------------------
def create_doc3():
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    
    # Left-aligned header with plain text URLs
    page.insert_text((50, 45), "Alex Chen", fontsize=20, fontname="helv")
    page.insert_text((50, 65), "Seattle, WA • alex.chen@example.com • 206-555-0144", fontsize=9.5, fontname="helv")
    page.insert_text((50, 80), "GitHub: github.com/alexchendev • LinkedIn: linkedin.com/in/alexchendev • Site: alexchen.dev", fontsize=9.5, fontname="helv")
    
    # Summary
    page.insert_text((50, 110), "SUMMARY", fontsize=12, fontname="helv")
    page.draw_line((50, 115), (560, 115), color=(0.7, 0.7, 0.7), width=1)
    page.insert_textbox(
        fitz.Rect(50, 125, 560, 155),
        "Backend developer specializing in data pipelines, database optimization, and scalable microservices with Python and Java.",
        fontsize=9.5, fontname="helv"
    )
    
    # Skills
    page.insert_text((50, 175), "TECHNICAL SKILLS", fontsize=12, fontname="helv")
    page.draw_line((50, 180), (560, 180), color=(0.7, 0.7, 0.7), width=1)
    page.insert_text((50, 200), "Python, Java, Spring Boot, MySQL, MongoDB, Kafka, Apache Spark, Linux, Docker", fontsize=9.5, fontname="helv")
    
    # Experience
    page.insert_text((50, 230), "EXPERIENCE", fontsize=12, fontname="helv")
    page.draw_line((50, 235), (560, 235), color=(0.7, 0.7, 0.7), width=1)
    page.insert_text((50, 255), "Data Engineer — DataPulse Systems", fontsize=10.5, fontname="helv")
    page.insert_text((460, 255), "2020 – 2023", fontsize=9.5, fontname="helv")
    exp_bullets = [
        "Constructed streaming ETL pipelines with Kafka and Spark ingesting 100GB logs hourly.",
        "Refactored MySQL schema queries resulting in a 65% reduction in report generation time."
    ]
    by = 275
    for b in exp_bullets:
        page.insert_textbox(fitz.Rect(60, by, 560, by + 22), f"•  {b}", fontsize=9, fontname="helv")
        by += 20
        
    # Projects
    page.insert_text((50, 335), "PROJECTS", fontsize=12, fontname="helv")
    page.draw_line((50, 340), (560, 340), color=(0.7, 0.7, 0.7), width=1)
    page.insert_text((50, 360), "Real-Time Telemetry Monitor | github.com/alexchendev/telemetry", fontsize=10, fontname="helv")
    page.insert_textbox(fitz.Rect(60, 375, 560, 400), "•  Built distributed sensor stream tracker in Python and Kafka with live dashboard alerts.", fontsize=9, fontname="helv")
    
    # Education
    page.insert_text((50, 420), "EDUCATION", fontsize=12, fontname="helv")
    page.draw_line((50, 425), (560, 425), color=(0.7, 0.7, 0.7), width=1)
    page.insert_text((50, 445), "B.S. in Information Systems — University of Washington", fontsize=10, fontname="helv")
    page.insert_text((480, 445), "2016 – 2020", fontsize=9.5, fontname="helv")
    
    pdf_path = os.path.join(HELDOUT_DIR, "doc3_unlinked_plain_urls.pdf")
    doc.save(pdf_path)
    doc.close()

    expected3 = {
        "personal_info": {
            "name": "Alex Chen",
            "email": "alex.chen@example.com",
            "phone": "206-555-0144",
            "location": "Seattle, WA",
            "github_url": "github.com/alexchendev",
            "linkedin_url": "linkedin.com/in/alexchendev",
            "portfolio_url": "alexchen.dev"
        },
        "summary": "Backend developer specializing in data pipelines, database optimization, and scalable microservices with Python and Java.",
        "expected_skills": ["Python", "Java", "Spring Boot", "MySQL", "MongoDB", "Kafka", "Apache Spark", "Linux", "Docker"],
        "experience": [
            {
                "company": "DataPulse Systems",
                "title": "Data Engineer",
                "start_date": "2020",
                "end_date": "2023"
            }
        ],
        "projects": [
            {
                "title": "Real-Time Telemetry Monitor",
                "url": "github.com/alexchendev/telemetry"
            }
        ],
        "education": [
            {
                "institution": "University of Washington",
                "degree": "B.S. in Information Systems"
            }
        ]
    }
    with open(os.path.join(HELDOUT_DIR, "doc3.expected.json"), "w", encoding="utf-8") as f:
        json.dump(expected3, f, indent=2)

# -------------------------------------------------------------
# Document 4: Fresher with achievements, percentages, no work experience
# -------------------------------------------------------------
def create_doc4():
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    
    # Header
    page.insert_text((50, 45), "Priya Sharma", fontsize=20, fontname="helv")
    page.insert_text((50, 65), "priya.sharma@example.com | +91 9876543210 | Mumbai, India", fontsize=9.5, fontname="helv")
    page.insert_text((50, 80), "github.com/priyasharma-dev | linkedin.com/in/priyasharma", fontsize=9.5, fontname="helv")
    
    # Education First (Typical for freshers)
    page.insert_text((50, 110), "EDUCATION", fontsize=12, fontname="helv")
    page.draw_line((50, 115), (560, 115), color=(0.7, 0.7, 0.7), width=1)
    page.insert_text((50, 135), "Bachelor of Technology in Computer Engineering", fontsize=10.5, fontname="helv")
    page.insert_text((470, 135), "2020 – 2024", fontsize=9.5, fontname="helv")
    page.insert_text((50, 150), "Veermata Jijabai Technological Institute (VJTI), Mumbai", fontsize=9.5, fontname="helv")
    page.insert_text((50, 165), "Aggregate Percentage: 87.4%", fontsize=9.5, fontname="helv")
    
    # Skills
    page.insert_text((50, 195), "SKILLS", fontsize=12, fontname="helv")
    page.draw_line((50, 200), (560, 200), color=(0.7, 0.7, 0.7), width=1)
    page.insert_text((50, 220), "Programming: C++, Java, Python, SQL, JavaScript", fontsize=9.5, fontname="helv")
    page.insert_text((50, 235), "Web & Databases: React, Node.js, Express, PostgreSQL, MongoDB, Git", fontsize=9.5, fontname="helv")
    
    # Academic Projects
    page.insert_text((50, 265), "ACADEMIC PROJECTS", fontsize=12, fontname="helv")
    page.draw_line((50, 270), (560, 270), color=(0.7, 0.7, 0.7), width=1)
    page.insert_text((50, 290), "Campus Placement Portal (React, Node.js, PostgreSQL)", fontsize=10, fontname="helv")
    page.insert_text((480, 290), "2023 – 2024", fontsize=9.5, fontname="helv")
    page.insert_textbox(fitz.Rect(60, 305, 560, 330), "•  Designed student application portal managing 1,200 candidate profiles with automated résumé screening.", fontsize=9, fontname="helv")
    
    page.insert_text((50, 345), "Smart Traffic Flow Predictor (Python, Scikit-learn)", fontsize=10, fontname="helv")
    page.insert_text((480, 345), "2023", fontsize=9.5, fontname="helv")
    page.insert_textbox(fitz.Rect(60, 360, 560, 385), "•  Implemented regression model forecasting intersection traffic density with 89.2% accuracy.", fontsize=9, fontname="helv")
    
    # Honors & Achievements (Custom Section)
    page.insert_text((50, 410), "HONORS & ACHIEVEMENTS", fontsize=12, fontname="helv")
    page.draw_line((50, 415), (560, 415), color=(0.7, 0.7, 0.7), width=1)
    achievements = [
        "Winner, Smart India Hackathon (SIH) 2023 out of 450 participating collegiate teams.",
        "Secured Global Rank 142 in CodeChef Starters Competition with over 8,000 global participants.",
        "Published technical paper on intelligent signal routing in IEEE Student Conference."
    ]
    ay = 430
    for a in achievements:
        page.insert_textbox(fitz.Rect(60, ay, 560, ay + 22), f"•  {a}", fontsize=9, fontname="helv")
        ay += 20
        
    pdf_path = os.path.join(HELDOUT_DIR, "doc4_fresher_achievements.pdf")
    doc.save(pdf_path)
    doc.close()

    expected4 = {
        "personal_info": {
            "name": "Priya Sharma",
            "email": "priya.sharma@example.com",
            "phone": "+91 9876543210",
            "location": "Mumbai, India",
            "github_url": "github.com/priyasharma-dev",
            "linkedin_url": "linkedin.com/in/priyasharma"
        },
        "education": [
            {
                "institution": "Veermata Jijabai Technological Institute (VJTI), Mumbai",
                "degree": "Bachelor of Technology in Computer Engineering",
                "grade": "87.4%"
            }
        ],
        "expected_skills": ["C++", "Java", "Python", "SQL", "JavaScript", "React", "Node.js", "Express", "PostgreSQL", "MongoDB", "Git"],
        "experience": [],
        "projects": [
            {
                "title": "Campus Placement Portal",
                "technologies": ["React", "Node.js", "PostgreSQL"]
            },
            {
                "title": "Smart Traffic Flow Predictor",
                "technologies": ["Python", "Scikit-learn"]
            }
        ],
        "custom_sections": ["HONORS & ACHIEVEMENTS"]
    }
    with open(os.path.join(HELDOUT_DIR, "doc4.expected.json"), "w", encoding="utf-8") as f:
        json.dump(expected4, f, indent=2)

# -------------------------------------------------------------
# Document 5: Scanned / Image Only (Zero text)
# -------------------------------------------------------------
def create_doc5():
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    # Draw shapes and colored rectangles to simulate a scanned image page without any selectable text
    page.draw_rect(fitz.Rect(50, 50, 562, 742), color=(0.95, 0.95, 0.95), fill=(0.93, 0.93, 0.93))
    page.draw_rect(fitz.Rect(80, 80, 300, 100), color=(0.4, 0.4, 0.4), fill=(0.4, 0.4, 0.4))
    page.draw_line((80, 120), (520, 120), color=(0.5, 0.5, 0.5), width=2)
    page.draw_rect(fitz.Rect(80, 140, 500, 200), color=(0.8, 0.8, 0.8), fill=(0.85, 0.85, 0.85))
    page.draw_rect(fitz.Rect(80, 230, 500, 350), color=(0.8, 0.8, 0.8), fill=(0.85, 0.85, 0.85))
    
    pdf_path = os.path.join(HELDOUT_DIR, "doc5_scanned_image_only.pdf")
    doc.save(pdf_path)
    doc.close()

    expected5 = {
        "is_scanned_image": True,
        "expected_status": "failed",
        "expected_error": "Could not parse text or structured data from uploaded PDF: Scanned image or non-selectable text PDF"
    }
    with open(os.path.join(HELDOUT_DIR, "doc5.expected.json"), "w", encoding="utf-8") as f:
        json.dump(expected5, f, indent=2)

if __name__ == "__main__":
    create_doc1()
    create_doc2()
    create_doc3()
    create_doc4()
    create_doc5()
    print("Created 5 held-out PDFs and handwritten expected JSON fixtures in:", HELDOUT_DIR)
