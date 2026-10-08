#!/usr/bin/env python3
"""Read-only validation of Pac-Man agent resources; not a filesystem permission lock."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / ".agents"
ALLOWLIST = {"src/search.py", "src/searchAgents.py"}
UNIVERSAL = {"change-safety", "validation"}
REQUIRED_RULES = UNIVERSAL | {
    "assignment", "search-algorithms", "testing", "grading",
    "report-submission", "git-ai-usage",
}
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def source_edit_permitted(
    policy: dict, paths: list[str], authorized: bool, operation: str = "edit",
) -> bool:
    """Evaluate a hypothetical request; the caller must establish human authorization."""
    return (
        authorized is True
        and operation == "edit"
        and bool(paths)
        and policy.get("sourceImplementationRequiresUserAuthorization") is True
        and policy.get("sourceEditExistingFilesOnly") is True
        and policy.get("srcFileCreationDeletionRenameForbidden") is True
        and policy.get("unauthorizedAgentChangesMustBeRejectedAndRestored") is True
        and policy.get("recoveryMustPreserveUserChanges") is True
        and set(policy.get("sourceEditAllowlist", [])) == ALLOWLIST
        and all(path in ALLOWLIST for path in paths)
        and all(
            (ROOT / path).is_file()
            and (ROOT / path).resolve().is_relative_to(ROOT)
            for path in paths
        )
    )


def validate_registry(registry: dict) -> list[str]:
    errors = []
    if registry.get("schema") != 1:
        errors.append("registry schema must be 1")
    policy = registry.get("policy", {})
    if not isinstance(policy, dict):
        return errors + ["registry policy must be an object"]
    for flag in (
        "projectRulesWin", "sourceImplementationRequiresUserAuthorization",
        "referenceProjectsAreReadOnly", "sourceEditExistingFilesOnly",
        "srcFileCreationDeletionRenameForbidden",
        "unauthorizedAgentChangesMustBeRejectedAndRestored",
        "recoveryMustPreserveUserChanges",
    ):
        if policy.get(flag) is not True:
            errors.append(f"policy must retain {flag}=true")
    allowed = policy.get("sourceEditAllowlist", [])
    if not isinstance(allowed, list) or len(allowed) != 2 or set(allowed) != ALLOWLIST:
        errors.append("source edit allowlist must contain exactly the two assignment files")
    if set(registry.get("universalRules", [])) != UNIVERSAL:
        errors.append("universal rules must include safety and validation")

    entries = registry.get("skills", [])
    if not isinstance(entries, list):
        return errors + ["registry skills must be a list"]
    ids = set()
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("skill entry must be an object")
            continue
        name = entry.get("id", "")
        if not isinstance(name, str) or not NAME.fullmatch(name):
            errors.append(f"invalid skill id: {name!r}")
            continue
        if name in ids:
            errors.append(f"duplicate skill id: {name}")
        ids.add(name)
        if entry.get("status") != "project":
            errors.append(f"{name}: only local project-authored skills are registered")
        if entry.get("localPath") != f".agents/skills/{name}":
            errors.append(f"{name}: skill path must match its repository-local folder")

    routes = registry.get("routes", [])
    if not isinstance(routes, list):
        return errors + ["routes must be a list"]
    route_ids = set()
    for route in routes:
        if not isinstance(route, dict):
            errors.append("route entry must be an object")
            continue
        route_id = route.get("id", "")
        if not isinstance(route_id, str) or not NAME.fullmatch(route_id):
            errors.append(f"invalid route id: {route_id!r}")
            continue
        if route_id in route_ids:
            errors.append(f"duplicate route id: {route_id}")
        route_ids.add(route_id)
        for rule in route.get("rules", []):
            if rule not in REQUIRED_RULES:
                errors.append(f"{route_id}: unknown rule {rule}")
        for skill in route.get("skills", []):
            if skill not in ids:
                errors.append(f"{route_id}: unregistered skill {skill}")
    for entry in entries:
        if isinstance(entry, dict) and entry.get("route") not in route_ids:
            errors.append(f"{entry.get('id')}: unknown owning route")
    return errors


def validate_cases(registry: dict, evaluations: dict) -> list[str]:
    errors = []
    if evaluations.get("schema") != 1:
        errors.append("evaluation schema must be 1")
    routes = {r["id"]: r for r in registry.get("routes", [])}
    cases = evaluations.get("cases", [])
    if not cases:
        errors.append("routing evaluations must contain cases")
    case_ids = set()
    for case in cases:
        case_id = case.get("id", "")
        if not case_id or case_id in case_ids:
            errors.append(f"missing or duplicate case id: {case_id}")
        case_ids.add(case_id)
        route = routes.get(case.get("route"))
        if route is None:
            errors.append(f"{case_id}: unknown route")
            continue
        for actual, expected in (
            ("skills", "expectedSkills"), ("rules", "expectedRules"),
        ):
            if set(route.get(actual, [])) != set(case.get(expected, [])):
                errors.append(f"{case_id}: {actual} routing differs from expectation")
        if not isinstance(case.get("sourceAuthorized"), bool):
            errors.append(f"{case_id}: authorization must be a boolean")
        paths = case.get("sourcePaths")
        if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
            errors.append(f"{case_id}: source paths must be a list of strings")
            continue
        permitted = source_edit_permitted(
            registry["policy"], paths, case.get("sourceAuthorized"),
            case.get("sourceOperation", "edit"),
        )
        if permitted is not case.get("expectedSourceEditPermitted"):
            errors.append(f"{case_id}: source permission result differs from expectation")
    return errors


def validate_files(registry: dict) -> list[str]:
    errors = []
    required = [
        ROOT / "AGENTS.md", AGENTS / "AGENTS.md", AGENTS / "README.md",
        AGENTS / "routing.md", AGENTS / "repository-map.md",
        AGENTS / "evals" / "routing-cases.json",
        AGENTS / "evals" / "test_source_guard.py",
        AGENTS / "scripts" / "source_guard.py",
    ] + [AGENTS / "rules" / f"{name}.md" for name in REQUIRED_RULES]
    for path in required:
        if not path.is_file():
            errors.append(f"missing resource: {path.relative_to(ROOT)}")
    for path in ALLOWLIST:
        if not (ROOT / path).is_file():
            errors.append(f"missing assignment file: {path}")

    registered = {entry["id"] for entry in registry["skills"]}
    discovered = {p.parent.name for p in (AGENTS / "skills").glob("*/SKILL.md")}
    if registered != discovered:
        errors.append(f"skill registry/discovery mismatch: {sorted(registered ^ discovered)}")
    for name in registered:
        path = AGENTS / "skills" / name / "SKILL.md"
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        front = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        if not front:
            errors.append(f"{name}: missing YAML discovery frontmatter")
            continue
        fields = dict(re.findall(r"(?m)^(name|description):\s*(.+)$", front.group(1)))
        if fields.get("name") != name or not fields.get("description", "").strip():
            errors.append(f"{name}: invalid name or missing discovery description")
        if len(name) >= 64:
            errors.append(f"{name}: skill name must be under 64 characters")

    markdown = [ROOT / "AGENTS.md"] + sorted(AGENTS.rglob("*.md"))
    for path in markdown:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            if target.startswith(("https://", "http://", "#")):
                continue
            destination = (path.parent / target.split("#", 1)[0]).resolve()
            if not destination.is_relative_to(ROOT) or not destination.exists():
                errors.append(f"{path.relative_to(ROOT)}: invalid local link {target}")
    routing = AGENTS / "routing.md"
    if routing.is_file():
        text = routing.read_text(encoding="utf-8")
        for route in registry["routes"]:
            if f"`{route['id']}`" not in text:
                errors.append(f"routing guide lacks route {route['id']}")
    return errors


def main() -> int:
    try:
        registry = json.loads((AGENTS / "registry" / "skills.json").read_text(encoding="utf-8"))
        evaluations = json.loads((AGENTS / "evals" / "routing-cases.json").read_text(encoding="utf-8"))
        errors = validate_registry(registry)
        if not errors:
            errors += validate_cases(registry, evaluations)
            errors += validate_files(registry)
    except (OSError, ValueError, TypeError, KeyError) as error:
        errors = [f"unable to validate agent resources: {error}"]
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(
        f"PASS: {len(REQUIRED_RULES)} rules, {len(registry['skills'])} skills, "
        f"{len(registry['routes'])} routes and {len(evaluations['cases'])} routing/permission cases"
    )
    print("PASS: links, skill metadata and the two-file source allowlist")
    print("Read-only guidance validation; no source permission is granted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
