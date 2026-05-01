import os
import zipfile
from io import BytesIO
from tempfile import TemporaryDirectory

from slugify import slugify

from reports.models import Evidence


def _safe_filename(name):
    base, ext = os.path.splitext(os.path.basename(name))
    safe_base = slugify(base) or "screenshot"
    return f"{safe_base}{ext.lower()}"


def _write_line(lines, text=""):
    lines.append(text)


def _code_block(lines, value, language=""):
    if not value:
        return
    fence = f"```{language}" if language else "```"
    _write_line(lines, fence)
    _write_line(lines, value.rstrip())
    _write_line(lines, "```")
    _write_line(lines)


def build_markdown_zip(machine):
    """
    Builds a ZIP containing report.md plus copied screenshot assets.
    Returns (zip_bytes, filename).
    """
    machine_slug = slugify(machine.name) or f"machine-{machine.pk}"

    with TemporaryDirectory() as tmp_dir:
        assets_dir = os.path.join(tmp_dir, "assets", "screenshots")
        os.makedirs(assets_dir, exist_ok=True)

        screenshot_paths = {}
        used_names = set()
        for screenshot in machine.screenshots.all():
            if not screenshot.image or not hasattr(screenshot.image, "path") or not os.path.exists(screenshot.image.path):
                continue

            filename = _safe_filename(screenshot.image.name)
            stem, ext = os.path.splitext(filename)
            counter = 2
            while filename in used_names:
                filename = f"{stem}-{counter}{ext}"
                counter += 1
            used_names.add(filename)

            destination = os.path.join(assets_dir, filename)
            with open(screenshot.image.path, "rb") as source, open(destination, "wb") as target:
                target.write(source.read())
            screenshot_paths[screenshot.pk] = f"assets/screenshots/{filename}"

        lines = []
        _write_line(lines, f"# {machine.name}")
        _write_line(lines)
        _write_line(lines, f"- Platform: {machine.platform}")
        _write_line(lines, f"- Difficulty: {machine.difficulty}")
        _write_line(lines, f"- OS: {machine.operating_system}")
        if machine.target_ip:
            _write_line(lines, f"- Target IP: `{machine.target_ip}`")
        if machine.author:
            _write_line(lines, f"- Author: {machine.author}")
        _write_line(lines)

        if machine.description:
            _write_line(lines, "## Overview")
            _write_line(lines)
            _write_line(lines, machine.description.strip())
            _write_line(lines)

        for phase_id, phase_name in Evidence.Phase.choices:
            if phase_id == Evidence.Phase.NOTES:
                continue
            evidences = list(machine.evidences.filter(phase=phase_id))
            phase_vulns = list(machine.vulnerabilities.all()) if phase_id == Evidence.Phase.VULN_ID else []
            phase_exploits = list(machine.exploits.all()) if phase_id == Evidence.Phase.EXPLOIT else []
            if not evidences and not phase_vulns and not phase_exploits:
                continue

            _write_line(lines, f"## {phase_name}")
            _write_line(lines)

            for vuln in phase_vulns:
                _write_line(lines, f"### Vulnerability: {vuln.title}")
                _write_line(lines)
                _write_line(lines, f"- Severity: {vuln.severity}")
                _write_line(lines, f"- Type: {vuln.vulnerability_type}")
                if vuln.cve:
                    _write_line(lines, f"- CVE: `{vuln.cve}`")
                if vuln.affected_service or vuln.affected_port:
                    _write_line(lines, f"- Affected: {vuln.affected_service} {vuln.affected_port}".strip())
                _write_line(lines)
                if vuln.how_identified:
                    _write_line(lines, vuln.how_identified.strip())
                    _write_line(lines)
                _code_block(lines, vuln.evidence)
                if vuln.impact:
                    _write_line(lines, f"Impact: {vuln.impact.strip()}")
                    _write_line(lines)
                if vuln.recommendation:
                    _write_line(lines, f"Recommendation: {vuln.recommendation.strip()}")
                    _write_line(lines)

            for exploit in phase_exploits:
                _write_line(lines, f"### Exploit: {exploit.name}")
                _write_line(lines)
                _write_line(lines, f"- Type: {exploit.exploit_type}")
                _write_line(lines, f"- Objective: {exploit.objective}")
                if exploit.cve:
                    _write_line(lines, f"- CVE: `{exploit.cve}`")
                if exploit.url:
                    _write_line(lines, f"- URL: {exploit.url}")
                _write_line(lines)
                if exploit.explanation:
                    _write_line(lines, exploit.explanation.strip())
                    _write_line(lines)
                _code_block(lines, exploit.command_used, "bash")
                _code_block(lines, exploit.output)
                if exploit.result:
                    _write_line(lines, f"Outcome: {exploit.result.strip()}")
                    _write_line(lines)

            for evidence in evidences:
                _write_line(lines, f"### {evidence.title}")
                _write_line(lines)
                if evidence.explanation:
                    _write_line(lines, evidence.explanation.strip())
                    _write_line(lines)
                _code_block(lines, evidence.command, "bash")
                _code_block(lines, evidence.output)
                for screenshot in evidence.screenshots.all():
                    path = screenshot_paths.get(screenshot.pk)
                    if path:
                        alt = screenshot.caption or screenshot.title or screenshot.image.name
                        _write_line(lines, f"![{alt}]({path})")
                        _write_line(lines)

        if machine.flags.exists():
            _write_line(lines, "## Flags")
            _write_line(lines)
            for flag in machine.flags.all():
                _write_line(lines, f"### {flag.flag_type}")
                _write_line(lines)
                value = "[censored]" if flag.censored else flag.value
                _write_line(lines, f"- Value: `{value}`")
                if flag.phase:
                    _write_line(lines, f"- Phase: {flag.get_phase_display()}")
                if flag.location:
                    _write_line(lines, f"- Location: `{flag.location}`")
                if flag.obtained_as_user:
                    _write_line(lines, f"- User: `{flag.obtained_as_user}`")
                _write_line(lines)
                _code_block(lines, flag.found_commands, "bash")
                if flag.notes:
                    _write_line(lines, flag.notes.strip())
                    _write_line(lines)

        notes = list(machine.evidences.filter(phase=Evidence.Phase.NOTES))
        if notes:
            _write_line(lines, "## Notes")
            _write_line(lines)
            for evidence in notes:
                _write_line(lines, f"### {evidence.title}")
                _write_line(lines)
                if evidence.explanation:
                    _write_line(lines, evidence.explanation.strip())
                    _write_line(lines)
                _code_block(lines, evidence.command, "bash")
                _code_block(lines, evidence.output)
                for screenshot in evidence.screenshots.all():
                    path = screenshot_paths.get(screenshot.pk)
                    if path:
                        alt = screenshot.caption or screenshot.title or screenshot.image.name
                        _write_line(lines, f"![{alt}]({path})")
                        _write_line(lines)

        gallery = [(screenshot, screenshot_paths.get(screenshot.pk)) for screenshot in machine.screenshots.all()]
        gallery = [(screenshot, path) for screenshot, path in gallery if path]
        if gallery:
            _write_line(lines, "## Screenshot Gallery")
            _write_line(lines)
            for screenshot, path in gallery:
                alt = screenshot.caption or screenshot.title or screenshot.image.name
                _write_line(lines, f"![{alt}]({path})")
                if screenshot.caption:
                    _write_line(lines, f"*{screenshot.caption}*")
                _write_line(lines)

        report_path = os.path.join(tmp_dir, "report.md")
        with open(report_path, "w", encoding="utf-8") as report:
            report.write("\n".join(lines).rstrip() + "\n")

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for root, _, files in os.walk(tmp_dir):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    archive.write(full_path, os.path.relpath(full_path, tmp_dir))
        buffer.seek(0)

    return buffer.getvalue(), f"{machine_slug}-markdown.zip"
