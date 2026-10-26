"""Generates 10 distinct synthetic PDF layout families using PyMuPDF (fitz)
to evaluate extraction robustness against layout variations, column formats,
spacings, alignments, and bullet mutations.
"""
import os
import fitz  # PyMuPDF


def create_layout_1(path: str):
    """Standard single-column with bold headings."""
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    y = 50
    page.insert_text((50, y), "ALEX MORGAN", fontsize=18, fontname="helv", fontfile=None)
    y += 20
    page.insert_text((50, y), "alex.morgan@testdomain.com | (555) 019-2834 | San Francisco, CA | linkedin.com/in/alexmorgan", fontsize=9, fontname="helv")
    y += 30

    sections = [
        ("SUMMARY", ["Versatile Senior Software Engineer with 7+ years of experience in distributed systems and backend engineering."]),
        ("SKILLS", ["Languages: Python, Go, TypeScript, SQL", "Frameworks: FastAPI, React, Node.js", "Tools: Docker, Kubernetes, AWS, PostgreSQL"]),
        ("EXPERIENCE", [
            "Senior Backend Engineer - CloudScale Systems (2021 - Present)",
            "• Architected scalable microservices handling over 50M requests per day.",
            "• Reduced database query latency by 42% through optimized indexing.",
            "Software Developer - TechNova Solutions (2018 - 2021)",
            "• Built real-time stream processing pipelines using Python and Kafka.",
            "• Implemented end-to-end automated testing suites with 95% code coverage.",
        ]),
        ("PROJECTS", [
            "MetricsEngine - Open Source Metrics Collector (2023)",
            "• Developed lightweight distributed metric ingestion engine in Go.",
            "• Utilized Redis and PostgreSQL for timeseries storage and aggregation.",
        ]),
        ("EDUCATION", [
            "B.S. in Computer Science - University of California, Berkeley (2014 - 2018)",
            "• GPA: 3.8 / 4.0 | Magna Cum Laude",
        ]),
        ("CERTIFICATIONS", [
            "AWS Certified Solutions Architect - Amazon Web Services (2022)",
        ]),
    ]

    for title, lines in sections:
        page.insert_text((50, y), title, fontsize=12, fontname="times-bold")
        y += 16
        for line in lines:
            page.insert_text((50, y), line, fontsize=9.5, fontname="times-roman")
            y += 14
        y += 12

    doc.save(path)
    doc.close()


def create_layout_2(path: str):
    """Centered uppercase headings with horizontal rules."""
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((220, 50), "BEATRICE CONNER", fontsize=16, fontname="times-bold")
    page.insert_text((180, 68), "beatrice.conner@email.com • 555-492-1100 • Seattle, WA", fontsize=9, fontname="times-roman")
    page.draw_line((50, 80), (562, 80))
    y = 100

    sections = [
        ("PROFESSIONAL EXPERIENCE", [
            "Lead Data Analyst - Insight Analytics Corp (Jun 2020 - Present)",
            "- Formulated predictive analytics models reducing customer churn by 18%.",
            "- Managed enterprise BI dashboards utilized by 200+ executive stakeholders.",
            "Data Analyst - Metro Financial Group (Jan 2017 - May 2020)",
            "- Built SQL extraction pipelines processing 10M+ transaction logs daily.",
            "- Conducted A/B tests to optimize credit card approval workflows.",
        ]),
        ("TECHNICAL SKILLS", [
            "Data Tools: Python, SQL, Tableau, Power BI, Excel",
            "Databases: Snowflake, PostgreSQL, BigQuery",
        ]),
        ("PROJECTS", [
            "Customer Retention Predictor (2022)",
            "- Implemented random forest classifier achieving 0.89 AUC-ROC.",
        ]),
        ("EDUCATION", [
            "M.S. in Applied Statistics - University of Washington (2015 - 2017)",
            "B.S. in Mathematics - Western Washington University (2011 - 2015)",
        ]),
        ("CERTIFICATIONS", [
            "Tableau Desktop Certified Professional - Tableau (2021)",
        ]),
    ]

    for title, lines in sections:
        page.insert_text((50, y), title, fontsize=11, fontname="times-bold")
        y += 4
        page.draw_line((50, y), (562, y))
        y += 14
        for line in lines:
            page.insert_text((50, y), line, fontsize=9.5, fontname="times-roman")
            y += 13
        y += 10

    doc.save(path)
    doc.close()


def create_layout_3(path: str):
    """Two-column sidebar layout (left sidebar, right body)."""
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    # Header across top
    page.insert_text((50, 45), "CARLOS MENDEZ", fontsize=16, fontname="helv")
    page.insert_text((50, 62), "carlos.m@example.com | San Jose, CA | github.com/carlosmendez", fontsize=9, fontname="helv")
    page.draw_line((50, 72), (562, 72))

    # Left sidebar background
    page.draw_rect(fitz.Rect(50, 80, 200, 750), color=None, fill=(0.96, 0.96, 0.96))

    # Sidebar Content
    page.insert_text((60, 100), "SKILLS", fontsize=10, fontname="times-bold")
    skills = ["Python", "JavaScript", "React", "Docker", "FastAPI", "MongoDB", "Linux", "Git"]
    sy = 118
    for s in skills:
        page.insert_text((65, sy), "• " + s, fontsize=8.5, fontname="helv")
        sy += 13

    page.insert_text((60, 250), "EDUCATION", fontsize=10, fontname="times-bold")
    page.insert_text((60, 268), "B.S. Software Eng", fontsize=8.5, fontname="helv")
    page.insert_text((60, 281), "San Jose State Univ", fontsize=8, fontname="helv")
    page.insert_text((60, 294), "2016 - 2020", fontsize=8, fontname="helv")

    page.insert_text((60, 330), "CERTIFICATIONS", fontsize=10, fontname="times-bold")
    page.insert_text((60, 348), "Docker Certified Associate", fontsize=8.5, fontname="helv")
    page.insert_text((60, 361), "Docker Inc (2021)", fontsize=8, fontname="helv")

    # Main Body Content
    by = 100
    page.insert_text((220, by), "WORK EXPERIENCE", fontsize=11, fontname="times-bold")
    by += 18
    page.insert_text((220, by), "Full Stack Software Engineer", fontsize=10, fontname="helv")
    by += 13
    page.insert_text((220, by), "Apex Innovations Inc | 2020 - Present", fontsize=8.5, fontname="helv")
    by += 14
    page.insert_text((220, by), "• Built responsive candidate portal using React and Tailwind CSS.", fontsize=8.5, fontname="helv")
    by += 13
    page.insert_text((220, by), "• Designed RESTful APIs in FastAPI with comprehensive OpenAPI documentation.", fontsize=8.5, fontname="helv")
    by += 13
    page.insert_text((220, by), "• Deployed multi-container services with Docker Compose and automated CI.", fontsize=8.5, fontname="helv")
    by += 22

    page.insert_text((220, by), "PROJECTS", fontsize=11, fontname="times-bold")
    by += 18
    page.insert_text((220, by), "Distributed Task Scheduler", fontsize=10, fontname="helv")
    by += 13
    page.insert_text((220, by), "• Implemented task queue system supporting cron intervals and worker nodes.", fontsize=8.5, fontname="helv")
    by += 13
    page.insert_text((220, by), "• Integrated Prometheus metrics for real-time latency monitoring.", fontsize=8.5, fontname="helv")

    doc.save(path)
    doc.close()


def create_layout_4(path: str):
    """Header with right-aligned contact details and left-aligned title."""
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((50, 50), "DANA V. KOWALSKI", fontsize=18, fontname="times-bold")
    page.insert_text((50, 68), "DevOps & Cloud Systems Architect", fontsize=10.5, fontname="times-italic")
    page.insert_text((380, 50), "dana.kowalski@devcloud.io", fontsize=9, fontname="helv")
    page.insert_text((380, 62), "+1 (555) 782-9930", fontsize=9, fontname="helv")
    page.insert_text((380, 74), "Austin, TX | github.com/danak", fontsize=9, fontname="helv")
    page.draw_line((50, 85), (562, 85))

    y = 105
    sections = [
        ("EXPERIENCE", [
            "Staff Infrastructure Architect - HyperCloud Services (2019 - Present)",
            "• Spearheaded Kubernetes multi-cluster migration across 3 AWS regions.",
            "• Reduced annual infrastructure spend by $320,000 using auto-scaling spot fleets.",
            "DevOps Engineer - BlueSky Software (2016 - 2019)",
            "• Maintained 99.99% uptime SLA across 40 production microservices.",
        ]),
        ("TECHNICAL EXPERTISE", [
            "Cloud: AWS, GCP, Azure, Terraform",
            "DevOps: Kubernetes, Docker, Helm, GitHub Actions",
            "Languages: Python, Bash, Go, HCL",
        ]),
        ("PROJECTS", [
            "Terraform AWS Landing Zone (2022)",
            "• Published automated compliant landing zone module with 15k+ downloads.",
        ]),
        ("EDUCATION", [
            "B.S. in Computer Engineering - University of Texas at Austin (2012 - 2016)",
        ]),
        ("CERTIFICATIONS", [
            "Certified Kubernetes Administrator (CKA) - Linux Foundation (2021)",
        ]),
    ]
    for title, lines in sections:
        page.insert_text((50, y), title, fontsize=11, fontname="times-bold")
        y += 15
        for l in lines:
            page.insert_text((50, y), l, fontsize=9.5, fontname="times-roman")
            y += 13
        y += 10

    doc.save(path)
    doc.close()


def create_layout_5_to_10(out_dir: str):
    """Generates remaining layout families 5 through 10 with various font and layout mutations."""
    # 5. Compact layout with pipe headers
    doc = fitz.open()
    p = doc.new_page(width=612, height=792)
    p.insert_text((50, 45), "ELENA ROSTOVA | Software Engineer | elena.rostova@tech.org | Chicago, IL", fontsize=10, fontname="helv")
    p.draw_line((50, 52), (562, 52))
    p.insert_text((50, 70), "SKILLS: Java, Spring Boot, MySQL, Kafka, Redis, Docker, Git", fontsize=9, fontname="helv")
    p.insert_text((50, 95), "EXPERIENCE", fontsize=11, fontname="helv")
    p.insert_text((50, 110), "Senior Software Engineer | FinTech Global | 2021 - Present", fontsize=9.5, fontname="helv")
    p.insert_text((50, 124), "• Engineered payment processing pipeline handling $2B in annual volume.", fontsize=9, fontname="helv")
    p.insert_text((50, 150), "PROJECTS", fontsize=11, fontname="helv")
    p.insert_text((50, 165), "LedgerEngine | 2023", fontsize=9.5, fontname="helv")
    p.insert_text((50, 179), "• High-throughput double-entry accounting ledger in Java and Spring.", fontsize=9, fontname="helv")
    p.insert_text((50, 205), "EDUCATION", fontsize=11, fontname="helv")
    p.insert_text((50, 220), "B.S. Computer Science | University of Illinois at Chicago | 2017 - 2021", fontsize=9, fontname="helv")
    p.insert_text((50, 245), "CERTIFICATIONS", fontsize=11, fontname="helv")
    p.insert_text((50, 260), "Oracle Certified Professional: Java SE 11 | Oracle | 2021", fontsize=9, fontname="helv")
    doc.save(os.path.join(out_dir, "layout_5_compact.pdf"))
    doc.close()

    # 6. Hyphenated dashed lists
    doc = fitz.open()
    p = doc.new_page(width=612, height=792)
    p.insert_text((50, 50), "FELIX ZHANG", fontsize=16, fontname="times-bold")
    p.insert_text((50, 68), "felix.zhang@datacenter.net | (555) 302-9114 | Boston, MA", fontsize=9.5, fontname="times-roman")
    p.insert_text((50, 95), "EXPERIENCE", fontsize=12, fontname="times-bold")
    p.insert_text((50, 112), "Systems Administrator at Vertex Networks (2018 - Present)", fontsize=10, fontname="times-italic")
    p.insert_text((60, 126), "- Administered 450+ physical and virtual Red Hat Linux enterprise servers.", fontsize=9.5, fontname="times-roman")
    p.insert_text((60, 139), "- Automated backup verification reducing manual admin intervention by 90%.", fontsize=9.5, fontname="times-roman")
    p.insert_text((50, 165), "SKILLS", fontsize=12, fontname="times-bold")
    p.insert_text((50, 180), "Linux, Bash, Ansible, Python, VMware, Networking, Nagios, Security", fontsize=9.5, fontname="times-roman")
    p.insert_text((50, 205), "PROJECTS", fontsize=12, fontname="times-bold")
    p.insert_text((50, 220), "AutoPatch - Linux Security Patching Tool (2022)", fontsize=10, fontname="times-italic")
    p.insert_text((60, 234), "- Automated safe zero-downtime rolling kernel updates across cluster.", fontsize=9.5, fontname="times-roman")
    p.insert_text((50, 260), "EDUCATION", fontsize=12, fontname="times-bold")
    p.insert_text((50, 275), "B.S. in Information Technology - Boston University (2014 - 2018)", fontsize=9.5, fontname="times-roman")
    p.insert_text((50, 300), "CERTIFICATIONS", fontsize=12, fontname="times-bold")
    p.insert_text((50, 315), "Red Hat Certified Engineer (RHCE) - Red Hat (2020)", fontsize=9.5, fontname="times-roman")
    doc.save(os.path.join(out_dir, "layout_6_dashed.pdf"))
    doc.close()

    # 7. Modern clean sans-serif with right-aligned dates
    doc = fitz.open()
    p = doc.new_page(width=612, height=792)
    p.insert_text((50, 50), "GABRIELLA SANTOS", fontsize=18, fontname="helv")
    p.insert_text((50, 68), "gabriella.santos@frontenddev.io | New York, NY | github.com/gabriellasantos", fontsize=9, fontname="helv")
    p.insert_text((50, 100), "WORK EXPERIENCE", fontsize=11, fontname="helv")
    p.insert_text((50, 116), "Frontend Team Lead", fontsize=10, fontname="helv")
    p.insert_text((50, 129), "Creative Pulse Media", fontsize=9, fontname="helv")
    p.insert_text((450, 116), "2021 - Present", fontsize=9, fontname="helv")
    p.insert_text((50, 143), "• Led team of 6 engineers revamping customer dashboard using Next.js.", fontsize=9, fontname="helv")
    p.insert_text((50, 170), "TECHNICAL SKILLS", fontsize=11, fontname="helv")
    p.insert_text((50, 185), "JavaScript, TypeScript, React, Next.js, HTML5, CSS3, Tailwind CSS, Jest", fontsize=9, fontname="helv")
    p.insert_text((50, 210), "PROJECTS", fontsize=11, fontname="helv")
    p.insert_text((50, 225), "UI Component Library", fontsize=10, fontname="helv")
    p.insert_text((450, 225), "2023", fontsize=9, fontname="helv")
    p.insert_text((50, 239), "• Accessible zero-dependency UI components with WCAG AAA conformance.", fontsize=9, fontname="helv")
    p.insert_text((50, 265), "EDUCATION", fontsize=11, fontname="helv")
    p.insert_text((50, 280), "B.A. in Digital Arts & Design - NYU (2017 - 2021)", fontsize=9, fontname="helv")
    p.insert_text((50, 305), "CERTIFICATIONS", fontsize=11, fontname="helv")
    p.insert_text((50, 320), "Meta Certified Front-End Developer - Meta (2022)", fontsize=9, fontname="helv")
    doc.save(os.path.join(out_dir, "layout_7_right_dates.pdf"))
    doc.close()

    # 8. All caps headings with tab stops
    doc = fitz.open()
    p = doc.new_page(width=612, height=792)
    p.insert_text((50, 50), "HAROLD KUMAR", fontsize=16, fontname="helv")
    p.insert_text((50, 68), "harold.kumar@securitylabs.com | Denver, CO", fontsize=9, fontname="helv")
    p.insert_text((50, 95), "EXPERIENCE", fontsize=11, fontname="helv")
    p.insert_text((50, 110), "Senior Security Engineer, CyberShield Inc (2019 - Present)", fontsize=9.5, fontname="helv")
    p.insert_text((50, 124), "• Conducted vulnerability assessments and penetration testing for Fortune 500 apps.", fontsize=9, fontname="helv")
    p.insert_text((50, 150), "SKILLS", fontsize=11, fontname="helv")
    p.insert_text((50, 165), "Cybersecurity, Penetration Testing, Python, Wireshark, Burp Suite, Cryptography", fontsize=9, fontname="helv")
    p.insert_text((50, 190), "PROJECTS", fontsize=11, fontname="helv")
    p.insert_text((50, 205), "NetAudit - Automated Port Scanner (2022)", fontsize=9.5, fontname="helv")
    p.insert_text((50, 219), "• High-speed asynchronous port scanner written in Python and Scapy.", fontsize=9, fontname="helv")
    p.insert_text((50, 245), "EDUCATION", fontsize=11, fontname="helv")
    p.insert_text((50, 260), "B.S. in Cybersecurity - University of Colorado Denver (2015 - 2019)", fontsize=9, fontname="helv")
    p.insert_text((50, 285), "CERTIFICATIONS", fontsize=11, fontname="helv")
    p.insert_text((50, 300), "Certified Information Systems Security Professional (CISSP) - (ISC)² (2021)", fontsize=9, fontname="helv")
    doc.save(os.path.join(out_dir, "layout_8_security.pdf"))
    doc.close()

    # 9. Two-page executive resume
    doc = fitz.open()
    p1 = doc.new_page(width=612, height=792)
    p1.insert_text((50, 50), "ISABELLA ROSSI", fontsize=18, fontname="times-bold")
    p1.insert_text((50, 68), "isabella.rossi@execsearch.com | Miami, FL | linkedin.com/in/isabellarossi", fontsize=9.5, fontname="times-roman")
    p1.insert_text((50, 100), "EXECUTIVE SUMMARY", fontsize=11, fontname="times-bold")
    p1.insert_text((50, 116), "Technology Executive with 12+ years directing engineering organizations of 100+ members.", fontsize=9.5, fontname="times-roman")
    p1.insert_text((50, 145), "EXPERIENCE", fontsize=11, fontname="times-bold")
    p1.insert_text((50, 160), "VP of Engineering - CloudVelocity (2018 - Present)", fontsize=10, fontname="times-italic")
    p1.insert_text((50, 174), "• Scaled distributed engineering team from 25 to 120 engineers across 4 hubs.", fontsize=9.5, fontname="times-roman")
    p1.insert_text((50, 188), "• Delivered enterprise SaaS platform generating $45M ARR.", fontsize=9.5, fontname="times-roman")
    p1.insert_text((50, 220), "SKILLS", fontsize=11, fontname="times-bold")
    p1.insert_text((50, 235), "Leadership, Agile, Software Architecture, Go, Python, Cloud Governance", fontsize=9.5, fontname="times-roman")

    p2 = doc.new_page(width=612, height=792)
    p2.insert_text((50, 50), "ISABELLA ROSSI - PAGE 2", fontsize=10, fontname="times-italic")
    p2.insert_text((50, 80), "PROJECTS", fontsize=11, fontname="times-bold")
    p2.insert_text((50, 95), "Enterprise Microservice Transformation (2021)", fontsize=10, fontname="times-italic")
    p2.insert_text((50, 109), "• Transitioned monolithic application to event-driven architecture.", fontsize=9.5, fontname="times-roman")
    p2.insert_text((50, 135), "EDUCATION", fontsize=11, fontname="times-bold")
    p2.insert_text((50, 150), "M.B.A. - Wharton School of Business (2014 - 2016)", fontsize=9.5, fontname="times-roman")
    p2.insert_text((50, 164), "B.S. in Computer Science - Columbia University (2008 - 2012)", fontsize=9.5, fontname="times-roman")
    p2.insert_text((50, 195), "CERTIFICATIONS", fontsize=11, fontname="times-bold")
    p2.insert_text((50, 210), "AWS Certified Solutions Architect Professional - Amazon Web Services (2020)", fontsize=9.5, fontname="times-roman")
    doc.save(os.path.join(out_dir, "layout_9_multipage.pdf"))
    doc.close()

    # 10. Academic / Research layout
    doc = fitz.open()
    p = doc.new_page(width=612, height=792)
    p.insert_text((50, 50), "DR. JULIAN VANCE", fontsize=16, fontname="times-bold")
    p.insert_text((50, 68), "julian.vance@ai-research.edu | Pittsburgh, PA", fontsize=9.5, fontname="times-roman")
    p.insert_text((50, 95), "RESEARCH EXPERIENCE", fontsize=11, fontname="times-bold")
    p.insert_text((50, 110), "Postdoctoral Researcher - Carnegie Mellon University (2021 - Present)", fontsize=9.5, fontname="times-italic")
    p.insert_text((50, 124), "• Published 4 peer-reviewed papers on transformer attention mechanisms in NeurIPS and ICML.", fontsize=9, fontname="times-roman")
    p.insert_text((50, 150), "TECHNICAL SKILLS", fontsize=11, fontname="times-bold")
    p.insert_text((50, 165), "PyTorch, JAX, Python, C++, CUDA, Distributed Training, NLP, Linear Algebra", fontsize=9, fontname="times-roman")
    p.insert_text((50, 190), "KEY PROJECTS", fontsize=11, fontname="times-bold")
    p.insert_text((50, 205), "FastAttention-CUDA (2023)", fontsize=9.5, fontname="times-italic")
    p.insert_text((50, 219), "• Custom CUDA kernels optimizing long-sequence multi-head attention.", fontsize=9, fontname="times-roman")
    p.insert_text((50, 245), "EDUCATION", fontsize=11, fontname="times-bold")
    p.insert_text((50, 260), "Ph.D. in Computer Science - Carnegie Mellon University (2016 - 2021)", fontsize=9, fontname="times-roman")
    p.insert_text((50, 285), "CERTIFICATIONS", fontsize=11, fontname="times-bold")
    p.insert_text((50, 300), "NVIDIA Deep Learning Institute Specialist - NVIDIA (2022)", fontsize=9, fontname="times-roman")
    doc.save(os.path.join(out_dir, "layout_10_research.pdf"))
    doc.close()


def generate_all(out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    create_layout_1(os.path.join(out_dir, "layout_1_single_col.pdf"))
    create_layout_2(os.path.join(out_dir, "layout_2_centered_rule.pdf"))
    create_layout_3(os.path.join(out_dir, "layout_3_sidebar.pdf"))
    create_layout_4(os.path.join(out_dir, "layout_4_header_split.pdf"))
    create_layout_5_to_10(out_dir)
    print(f"Successfully generated 10 synthetic layout PDFs in {out_dir}")


if __name__ == "__main__":
    target = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "synthetic")
    generate_all(os.path.abspath(target))
