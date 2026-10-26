import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.services.ai.ollama_provider import OllamaProvider, ollama_provider
from tests.test_tailoring import create_authenticated_user_with_profile


@pytest.mark.asyncio
async def test_custom_instruction_passes_to_ollama_unmodified():
    provider = OllamaProvider(base_url="http://mock-ollama:11434", model="qwen3:4b-instruct")
    custom_prompt = "Convert this into 3 concise bullet points focusing on system observability."

    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = lambda: {
        "response": (
            '{"suggested_text": "• Configured Prometheus metrics.\\n• Set up Grafana dashboards.\\n• Optimized log pipeline.", '
            '"explanation": "Converted to 3 bullet points focused on observability."}'
        )
    }

    with patch.object(provider, "check_unsupported_evidence", return_value=[]):
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            result = await provider.refine_section(
                section="experience",
                instruction=custom_prompt,
                current_text="Managed logging and metrics.",
                context_skills=["Prometheus", "Grafana", "Python"],
            )

            assert mock_post.called
            call_args = mock_post.call_args[1]
            sent_payload = call_args["json"]
            assert sent_payload["model"] == "qwen3:4b-instruct"
            assert custom_prompt in sent_payload["prompt"]
            assert sent_payload["keep_alive"] == "15m"
            assert "SPECIAL RULE FOR SUMMARY" not in sent_payload["prompt"]

            assert "• Configured Prometheus metrics." in result["suggested_text"]
            assert result["has_unsupported_content"] is False


@pytest.mark.asyncio
async def test_unsupported_evidence_triggers_warning():
    provider = OllamaProvider(base_url="http://mock-ollama:11434", model="qwen3:4b-instruct")
    instruction = "Add that I am an AWS Certified Solutions Architect and deployed Kubernetes."

    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = lambda: {
        "response": (
            '{"suggested_text": "Led deployment of Kubernetes on AWS and achieved AWS Solutions Architect certification.", '
            '"explanation": "Added requested Kubernetes and AWS credentials."}'
        )
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        # Candidate only has Python, PostgreSQL, Docker in evidence
        result = await provider.refine_section(
            section="experience",
            instruction=instruction,
            current_text="Built backend systems in Python.",
            candidate_evidence={"skills": ["Python", "PostgreSQL", "Docker"]},
            context_skills=["Python", "PostgreSQL", "Docker"],
            acknowledge_unsupported=False,
        )

        assert result["has_unsupported_content"] is True
        assert len(result["missing_evidence"]) > 0
        assert any("Kubernetes" in s or "AWS" in s for s in result["missing_evidence"])
        assert result["evidence_warning"] is not None
        assert "unverified" in result["evidence_warning"].lower()


@pytest.mark.asyncio
async def test_acknowledged_unsupported_evidence_allows_proceeding():
    provider = OllamaProvider(base_url="http://mock-ollama:11434", model="qwen3:4b-instruct")
    instruction = "Add that I am an AWS Certified Solutions Architect and deployed Kubernetes."

    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = lambda: {
        "response": (
            '{"suggested_text": "Led deployment of Kubernetes on AWS and achieved AWS Solutions Architect certification.", '
            '"explanation": "Added requested credentials."}'
        )
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        result = await provider.refine_section(
            section="experience",
            instruction=instruction,
            current_text="Built backend systems in Python.",
            candidate_evidence={"skills": ["Python", "Docker"]},
            context_skills=["Python", "Docker"],
            acknowledge_unsupported=True,
        )

        assert result["has_unsupported_content"] is True
        # Warning is cleared because the user explicitly acknowledged
        assert result["evidence_warning"] is None
        assert "Kubernetes" in result["suggested_text"]


def test_deterministic_fallback_handles_diverse_instructions():
    provider = OllamaProvider()

    # 1. Concise
    concise_res = provider.deterministic_refine_section(
        section="summary",
        instruction="Make this concise and one line.",
        current_text="Experienced engineer who designed scalable microservices. Built distributed pipelines. Led team.",
    )
    assert len(concise_res["suggested_text"].splitlines()) == 1
    assert "Experienced engineer" in concise_res["suggested_text"]

    # 2. Bullet points
    bullet_res = provider.deterministic_refine_section(
        section="experience",
        instruction="Convert this into bullet points.",
        current_text="Designed scalable APIs. Maintained CI/CD pipelines.",
    )
    assert "• " in bullet_res["suggested_text"]

    # 3. Constructive feedback
    feedback_res = provider.deterministic_refine_section(
        section="summary",
        instruction="Give me feedback on this section.",
        current_text="I am a backend developer.",
    )
    assert "Feedback" in feedback_res["suggested_text"]
    assert "Strengths" in feedback_res["suggested_text"]

    # 4. Simpler language
    simple_res = provider.deterministic_refine_section(
        section="projects",
        instruction="Explain in simpler language without jargon.",
        current_text="Spearheaded distributed high-throughput architecture.",
    )
    assert "Led" in simple_res["suggested_text"] or "designed" in simple_res["suggested_text"].lower()


def test_api_ask_ai_edit_with_evidence_warning_and_ack(client: TestClient):
    headers = create_authenticated_user_with_profile(client, "ai_evidence@test.com", "Evidence Candidate")

    job_res = client.post(
        "/api/v1/jobs",
        json={"company": "Cloud Corp", "title": "DevOps Engineer", "raw_jd_text": "DevOps role."},
        headers=headers,
    )
    job_id = job_res.json()["id"]

    tailor_res = client.post(f"/api/v1/jobs/{job_id}/tailor", headers=headers)
    resume_id = tailor_res.json()["id"]

    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = lambda: {
        "response": (
            '{"suggested_text": "Architected Kubernetes deployments on AWS with automated Terraform pipelines.", '
            '"explanation": "Enhanced cloud infrastructure experience."}'
        )
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        # Request introducing unverified AWS/Kubernetes without acknowledgment
        res1 = client.post(
            f"/api/v1/tailored-resumes/{resume_id}/edit",
            json={
                "section": "experience",
                "instruction": "Add that I am an expert in Kubernetes and AWS cloud infrastructure.",
                "current_text": "Managed Linux servers and Docker containers.",
                "acknowledge_unsupported": False,
            },
            headers=headers,
        )
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["section"] == "experience"
        assert "suggested_text" in data1
        assert data1["has_unsupported_content"] is True
        assert data1["evidence_warning"] is not None
        assert len(data1["missing_evidence"]) > 0

        # Re-request with acknowledgment
        res2 = client.post(
            f"/api/v1/tailored-resumes/{resume_id}/edit",
            json={
                "section": "experience",
                "instruction": "Add that I am an expert in Kubernetes and AWS cloud infrastructure.",
                "current_text": "Managed Linux servers and Docker containers.",
                "acknowledge_unsupported": True,
            },
            headers=headers,
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["evidence_warning"] is None
        assert data2["has_unsupported_content"] is True
