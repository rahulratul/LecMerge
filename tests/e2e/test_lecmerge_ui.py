"""Selenium end-to-end smoke test covering the full LecMerge GUI workflow (Section 9.4)."""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_server(url: str, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError(f"Server did not become ready at {url} within {timeout}s")


@pytest.mark.e2e
def test_lecmerge_end_to_end_gui_workflow() -> None:
    tmp_dir = Path(tempfile.mkdtemp(prefix="lecmerge-e2e-"))
    db_file = tmp_dir / "e2e.db"
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    screenshot_dir = os.environ.get("LECMERGE_SCREENSHOT_DIR")

    env = os.environ.copy()
    env["LECMERGE_DATABASE_URL"] = f"sqlite:///{db_file}"

    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    driver = None
    try:
        _wait_for_server(base_url)

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,900")
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 10)

        def snap(name: str) -> None:
            if screenshot_dir:
                Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
                driver.save_screenshot(str(Path(screenshot_dir) / name))

        # 1. Open dashboard
        driver.get(base_url)
        wait.until(EC.presence_of_element_located((By.ID, "courses-empty")))
        snap("01_dashboard_empty.png")

        # 2. Create one course
        driver.find_element(By.ID, "course-code").send_keys("CSE 3206")
        driver.find_element(By.ID, "course-title").send_keys("Software Engineering Sessional")
        driver.find_element(By.ID, "course-submit-btn").click()
        wait.until(EC.presence_of_element_located((By.ID, "create-lecture-form")))
        assert "CSE 3206" in driver.page_source

        # 3. Create one lecture with two ordered blocks
        driver.find_element(By.ID, "lecture-title").send_keys("Lecture 4: Design Patterns")
        driver.find_element(By.ID, "lecture-date").send_keys("2026-11-28")
        driver.find_element(By.ID, "lecture-topics").send_keys("Composite Pattern\nStrategy Pattern")
        driver.find_element(By.ID, "lecture-submit-btn").click()
        wait.until(EC.presence_of_element_located((By.ID, "block-list")))
        assert "Composite Pattern" in driver.page_source
        assert "Strategy Pattern" in driver.page_source

        # 4. Open first block and submit two conflicting formula fragments
        driver.find_element(By.LINK_TEXT, "Composite Pattern").click()
        wait.until(EC.presence_of_element_located((By.ID, "fragment-author")))

        driver.find_element(By.ID, "fragment-author").send_keys("Amina")
        driver.find_element(By.ID, "fragment-content").send_keys("F = ma")
        driver.find_element(By.ID, "fragment-submit-btn").click()
        wait.until(EC.presence_of_element_located((By.ID, "fragment-list")))

        driver.find_element(By.ID, "fragment-author").send_keys("Tariq")
        driver.find_element(By.ID, "fragment-content").send_keys("F = m * a^2\nDetailed derivation for exam review.")
        driver.find_element(By.ID, "fragment-submit-btn").click()
        wait.until(EC.presence_of_element_located((By.ID, "conflict-warning")))

        # 5. Verify both fragments remain visible and potential-conflict warning appears
        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Amina" in page_text
        assert "Tariq" in page_text
        assert "F = ma" in page_text
        assert "Detailed derivation for exam review." in page_text
        assert "Potential formula conflict — review required" in page_text
        snap("04_block_conflict.png")

        # 6. Check lecture workspace shows blind spot for block 2 and conflict warning for block 1
        driver.find_element(By.LINK_TEXT, "Back to lecture").click()
        wait.until(EC.presence_of_element_located((By.ID, "block-list")))
        ws_text = driver.find_element(By.TAG_NAME, "body").text
        assert "50.0%" in ws_text
        assert "BLIND SPOT" in ws_text
        assert "Potential formula conflict — review required" in ws_text
        snap("02_lecture_workspace.png")

        # 7. Open first block, select Most Detailed, and merge
        driver.find_element(By.LINK_TEXT, "Composite Pattern").click()
        wait.until(EC.presence_of_element_located((By.ID, "merge-strategy-select")))
        Select(driver.find_element(By.ID, "merge-strategy-select")).select_by_value("most_detailed")
        driver.find_element(By.ID, "merge-submit-btn").click()

        # 8. Verify canonical merged content is shown and both original fragments remain visible
        wait.until(EC.presence_of_element_located((By.ID, "canonical-content")))
        merged_body = driver.find_element(By.ID, "merged-content-body").text
        assert "Detailed derivation for exam review." in merged_body
        fragments_text = driver.find_element(By.ID, "fragment-list").text
        assert "Amina" in fragments_text
        assert "Tariq" in fragments_text
        snap("05_block_merged.png")

        # 9. Open study sheet and verify content and download link
        driver.find_element(By.LINK_TEXT, "Back to lecture").click()
        wait.until(EC.presence_of_element_located((By.ID, "study-sheet-link")))
        driver.find_element(By.ID, "study-sheet-link").click()
        wait.until(EC.presence_of_element_located((By.ID, "study-sheet-markdown")))

        md_text = driver.find_element(By.ID, "study-sheet-markdown").text
        assert "# Lecture 4: Design Patterns" in md_text
        assert "Detailed derivation for exam review." in md_text
        assert "Potential formula conflict — review required" in md_text
        assert "Blind spot" in md_text

        dl_link = driver.find_element(By.ID, "study-sheet-download-link")
        assert dl_link.get_attribute("href").endswith("/study-sheet/download")
        snap("06_study_sheet.png")

        if screenshot_dir:
            driver.get(base_url)
            wait.until(EC.presence_of_element_located((By.ID, "course-list")))
            snap("01_dashboard.png")
            driver.get(f"{base_url}/docs")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".swagger-ui")))
            time.sleep(1.0)
            snap("07_swagger_docs.png")
    finally:
        if driver is not None:
            driver.quit()
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
        shutil.rmtree(tmp_dir, ignore_errors=True)
