"""
Content quality and repository structure tests for ecommerce-ai-skills.

Uses pytest to verify:
- _config.yml metadata correctness (Req 1.1, 1.2)
- Required directory structure (Req 5.1)
- README line count (Req 5.4)
- Prompt template minimum count (Req 6.3)
- Jekyll SEO plugin config (Req 9.3)
- Roadmap non-empty (Req 2.4)
- Internal link integrity in README.md
"""

import re
from pathlib import Path

import yaml

# Repo root is the parent of the tests/ directory
REPO_ROOT = Path(__file__).parent.parent


def _load_config():
    """Load and parse _config.yml."""
    config_path = REPO_ROOT / "_config.yml"
    assert config_path.exists(), "_config.yml not found"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# --- _config.yml metadata tests ---


def test_config_title():
    """Verify _config.yml title contains expected keywords."""
    config = _load_config()
    title = config.get("title", "")
    assert "ecommerce-ai-skills" in title, f"Title missing 'ecommerce-ai-skills': {title}"
    assert "Knowledge Hub" in title, f"Title missing 'Knowledge Hub': {title}"


def test_config_description():
    """Verify _config.yml description contains both Chinese and English text."""
    config = _load_config()
    desc = config.get("description", "")
    has_chinese = bool(re.search(r"[\u4e00-\u9fff]", desc))
    has_english = bool(re.search(r"[a-zA-Z]{3,}", desc))
    assert has_chinese, f"Description missing Chinese text: {desc}"
    assert has_english, f"Description missing English text: {desc}"


# --- Directory structure tests ---


def test_paths_directory_structure():
    """Verify paths/a-operators/, paths/b-developers/, paths/c-managers/ directories exist."""
    for subdir in ["a-operators", "b-developers", "c-managers"]:
        path = REPO_ROOT / "paths" / subdir
        assert path.is_dir(), f"Missing directory: paths/{subdir}/"


def test_path_a_modules():
    """Verify a1 through a6 .md files exist in paths/a-operators/."""
    base = REPO_ROOT / "paths" / "a-operators"
    expected = [
        "a1-product-research.md",
        "a2-listing-optimization.md",
        "a3-advertising.md",
        "a4-customer-service.md",
        "a5-inventory.md",
        "a6-compliance.md",
    ]
    for filename in expected:
        assert (base / filename).is_file(), f"Missing file: paths/a-operators/{filename}"


def test_path_b_modules():
    """Verify b1 through b5 .md files exist in paths/b-developers/."""
    base = REPO_ROOT / "paths" / "b-developers"
    expected = [
        "b1-data-pipeline.md",
        "b2-prediction-models.md",
        "b3-rag-knowledge-base.md",
        "b4-agent-workflow.md",
        "b5-local-model-deploy.md",
    ]
    for filename in expected:
        assert (base / filename).is_file(), f"Missing file: paths/b-developers/{filename}"


def test_path_c_modules():
    """Verify c1 through c3 .md files exist in paths/c-managers/."""
    base = REPO_ROOT / "paths" / "c-managers"
    expected = [
        "c1-ai-assessment.md",
        "c2-team-building.md",
        "c3-roi-evaluation.md",
    ]
    for filename in expected:
        assert (base / filename).is_file(), f"Missing file: paths/c-managers/{filename}"


# --- README tests ---


def test_readme_line_count():
    """Verify README.md is under 500 lines."""
    readme = REPO_ROOT / "README.md"
    assert readme.is_file(), "README.md not found"
    line_count = len(readme.read_text(encoding="utf-8").splitlines())
    assert line_count < 500, f"README.md has {line_count} lines (limit: 500)"


# --- Prompts tests ---


def test_prompts_minimum_count():
    """Verify prompts/ directory has at least 4 .md files (excluding README.md)."""
    prompts_dir = REPO_ROOT / "prompts"
    assert prompts_dir.is_dir(), "prompts/ directory not found"
    md_files = [
        f for f in prompts_dir.glob("*.md") if f.name.lower() != "readme.md"
    ]
    assert len(md_files) >= 4, (
        f"prompts/ has {len(md_files)} template files (minimum: 4). "
        f"Found: {[f.name for f in md_files]}"
    )


def test_prompts_index_exists():
    """Verify prompts/README.md exists."""
    assert (REPO_ROOT / "prompts" / "README.md").is_file(), "prompts/README.md not found"


# --- Roadmap tests ---


def test_roadmap_not_empty():
    """Verify roadmap/ directory has at least one non-empty .md file."""
    roadmap_dir = REPO_ROOT / "roadmap"
    assert roadmap_dir.is_dir(), "roadmap/ directory not found"
    md_files = list(roadmap_dir.glob("*.md"))
    assert md_files, "roadmap/ has no .md files"
    has_non_empty = any(f.stat().st_size > 0 for f in md_files)
    assert has_non_empty, "All .md files in roadmap/ are empty"


# --- Jekyll SEO tests ---


def test_jekyll_seo_plugins():
    """Verify _config.yml plugins list includes jekyll-seo-tag and jekyll-sitemap."""
    config = _load_config()
    plugins = config.get("plugins", [])
    assert "jekyll-seo-tag" in plugins, f"Missing jekyll-seo-tag in plugins: {plugins}"
    assert "jekyll-sitemap" in plugins, f"Missing jekyll-sitemap in plugins: {plugins}"


# --- Internal link integrity ---


def test_no_broken_internal_links():
    """Scan README.md for relative path links and verify each target exists."""
    readme = REPO_ROOT / "README.md"
    assert readme.is_file(), "README.md not found"
    content = readme.read_text(encoding="utf-8")

    # Match [text](relative/path) — skip URLs (http/https), anchors (#), and mailto
    link_pattern = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    broken = []

    for match in link_pattern.finditer(content):
        text, target = match.group(1), match.group(2)
        # Skip external URLs, anchors, and mailto links
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        # Strip anchor fragment from path
        clean_target = target.split("#")[0]
        if not clean_target:
            continue
        target_path = REPO_ROOT / clean_target
        if not target_path.exists():
            broken.append(f"[{text}]({target}) -> {clean_target}")

    assert not broken, (
        f"Found {len(broken)} broken internal link(s) in README.md:\n"
        + "\n".join(f"  - {b}" for b in broken)
    )


# =============================================================================
# Phase 2 tests
# =============================================================================


# --- README_EN.md tests (Req 4.1) ---


def test_readme_en_exists():
    """Verify README_EN.md exists."""
    assert (REPO_ROOT / "README_EN.md").is_file(), "README_EN.md not found"


# --- Community infrastructure tests ---


def test_codeowners_exists():
    """Verify CODEOWNERS file exists (Req 8.3)."""
    assert (REPO_ROOT / "CODEOWNERS").is_file(), "CODEOWNERS not found"


def test_changelog_exists():
    """Verify CHANGELOG.md exists (Req 10.5)."""
    assert (REPO_ROOT / "CHANGELOG.md").is_file(), "CHANGELOG.md not found"


# --- Notebooks tests (Req 7.5) ---


def test_notebooks_readme_exists():
    """Verify notebooks/README.md exists."""
    assert (REPO_ROOT / "notebooks" / "README.md").is_file(), "notebooks/README.md not found"


# --- Issue templates tests (Req 8.1) ---


def test_issue_templates_exist():
    """Verify required Issue templates exist in .github/ISSUE_TEMPLATE/."""
    template_dir = REPO_ROOT / ".github" / "ISSUE_TEMPLATE"
    assert template_dir.is_dir(), ".github/ISSUE_TEMPLATE/ directory not found"

    required_templates = [
        "broken_link_report.md",
        "prompt_submission.md",
        "notebook_submission.md",
        "feature_request.md",
    ]
    for template in required_templates:
        assert (template_dir / template).is_file(), (
            f"Missing Issue template: .github/ISSUE_TEMPLATE/{template}"
        )


# --- Case studies tests (Req 10.1) ---


def test_case_studies_minimum_count():
    """Verify docs/case-studies/ has at least 2 case study files (excluding README.md)."""
    case_dir = REPO_ROOT / "docs" / "case-studies"
    assert case_dir.is_dir(), "docs/case-studies/ directory not found"
    md_files = [
        f for f in case_dir.glob("*.md") if f.name.lower() != "readme.md"
    ]
    assert len(md_files) >= 2, (
        f"docs/case-studies/ has {len(md_files)} case study files (minimum: 2). "
        f"Found: {[f.name for f in md_files]}"
    )
