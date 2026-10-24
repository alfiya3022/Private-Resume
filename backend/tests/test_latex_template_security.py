"""Regression tests for custom LaTeX template upload and compilation safety."""
from io import BytesIO
from types import SimpleNamespace
import zipfile

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.config import settings
from app.services import latex_service as latex_service_module
from app.services.latex_service import LatexService, latex_service


def _make_zip(files: dict[str, bytes]) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def _auth_headers(client: TestClient, email: str = "template_upload@test.local") -> dict[str, str]:
    password = "SecurePassword123!"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Template Candidate"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture

def template_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_DIR", str(tmp_path))
    return tmp_path


def test_template_upload_rejects_empty_file(client: TestClient):
    headers = _auth_headers(client, "empty_template@test.local")
    response = client.post(
        "/api/v1/profile/template",
        headers=headers,
        files={"file": ("empty.tex", b"", "application/x-tex")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty."


def test_template_upload_rejects_oversized_file_before_full_read(client: TestClient):
    headers = _auth_headers(client, "oversized_template@test.local")
    response = client.post(
        "/api/v1/profile/template",
        headers=headers,
        files={"file": ("large.tex", b"x" * (10 * 1024 * 1024 + 1), "application/x-tex")},
    )
    assert response.status_code == 413
    assert "10 MB" in response.json()["detail"]


def test_template_service_rejects_corrupted_zip_without_replacing_existing_template(template_storage):
    latex_service.save_user_template(41, "existing.tex", b"\\documentclass{article}\\begin{document}Existing\\end{document}")
    existing_path = latex_service.get_custom_template_path(41)
    assert existing_path is not None
    original_content = existing_path.read_bytes()

    with pytest.raises(HTTPException) as error:
        latex_service.save_user_template(41, "broken.zip", b"this is not a zip archive")

    assert error.value.status_code == 400
    assert existing_path.read_bytes() == original_content


def test_template_service_rejects_zip_path_traversal_without_writing_outside_storage(template_storage):
    archive = _make_zip({"../escaped.tex": b"malicious", "main.tex": b"\\documentclass{article}\\begin{document}Safe\\end{document}"})

    with pytest.raises(HTTPException) as error:
        latex_service.save_user_template(42, "unsafe.zip", archive)

    assert error.value.status_code == 400
    assert not (template_storage / "escaped.tex").exists()
    assert latex_service.get_custom_template_path(42) is None


def test_template_service_rejects_zip_without_tex_and_preserves_previous_template(template_storage):
    latex_service.save_user_template(43, "existing.tex", b"\\documentclass{article}\\begin{document}Existing\\end{document}")
    existing_path = latex_service.get_custom_template_path(43)
    assert existing_path is not None
    original_content = existing_path.read_bytes()

    with pytest.raises(HTTPException) as error:
        latex_service.save_user_template(43, "no_tex.zip", _make_zip({"readme.txt": b"No TeX here"}))

    assert error.value.status_code == 400
    assert existing_path.read_bytes() == original_content


def test_template_service_installs_valid_zip_and_preserves_relative_dependencies(template_storage):
    archive = _make_zip({
        "main.tex": b"\\documentclass{article}\\begin{document}Valid\\end{document}",
        "sections/experience.tex": b"Experience section",
    })

    result = latex_service.save_user_template(44, "valid.zip", archive)
    template_dir = template_storage / "templates" / "44"

    assert result["status"] == "success"
    assert (template_dir / "main.tex").is_file()
    assert (template_dir / "sections" / "experience.tex").read_bytes() == b"Experience section"


def test_compile_pdf_surfaces_latex_compilation_failure(tmp_path, monkeypatch):
    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="! Undefined control sequence")

    monkeypatch.setattr(latex_service_module.subprocess, "run", fake_run)

    with pytest.raises(HTTPException) as error:
        LatexService().compile_pdf(
            r"\documentclass{article}\begin{document}\badcommand\end{document}",
            "resume",
            tmp_path,
        )

    assert error.value.status_code == 500
    assert "Compilation error" in error.value.detail
    assert "Undefined control sequence" in error.value.detail


def test_template_service_rejects_archive_with_too_many_files(template_storage):
    files = {f"file_{i}.txt": b"content" for i in range(105)}
    files["main.tex"] = b"\\documentclass{article}\\begin{document}Content\\end{document}"
    archive = _make_zip(files)

    with pytest.raises(HTTPException) as error:
        latex_service.save_user_template(50, "too_many_files.zip", archive)

    assert error.value.status_code == 400
    assert "too many files" in error.value.detail


def test_template_service_rejects_archive_with_absolute_paths(template_storage):
    archive = _make_zip({"/absolute/main.tex": b"\\documentclass{article}\\begin{document}Unsafe\\end{document}"})

    with pytest.raises(HTTPException) as error:
        latex_service.save_user_template(51, "absolute_path.zip", archive)

    assert error.value.status_code == 400
    assert "unsafe path" in error.value.detail


def test_template_service_rejects_archive_with_symlinks(template_storage):
    import stat
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        zip_info = zipfile.ZipInfo("symlink.tex")
        zip_info.create_system = 3  # Unix
        zip_info.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive.writestr(zip_info, "/etc/passwd")
        archive.writestr("main.tex", b"\\documentclass{article}\\begin{document}Safe\\end{document}")

    with pytest.raises(HTTPException) as error:
        latex_service.save_user_template(52, "symlink.zip", buffer.getvalue())

    assert error.value.status_code == 400
    assert "Symbolic links are not allowed" in error.value.detail
