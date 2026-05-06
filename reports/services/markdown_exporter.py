import os
import zipfile
from io import BytesIO
from tempfile import TemporaryDirectory

from slugify import slugify
from django.utils import translation

from reports.models import Evidence
from reports.services.i18n import get_i18n


def _safe_filename(name):
    base, ext = os.path.splitext(os.path.basename(name))
    safe_base = slugify(base) or "screenshot"
    return f"{safe_base}{ext.lower()}"


def _write_line(lines, text=""):
    lines.append(text)


def _section(lines, title):
    if lines:
        _write_line(lines, "___")
        _write_line(lines)
    _write_line(lines, f"## {title}")
    _write_line(lines)


def _code_block(lines, value, language=""):
    if not value:
        return
    fence = f"```{language}" if language else "```"
    _write_line(lines, fence)
    _write_line(lines, value.rstrip())
    _write_line(lines, "```")
    _write_line(lines)


def _phase_title(i18n, phase_id):
    return i18n.get(f"{phase_id}_phase", phase_id.replace("_", " ").title())


def _write_screenshots(lines, screenshots, screenshot_paths):
    for screenshot in screenshots:
        path = screenshot_paths.get(screenshot.pk)
        if path:
            alt = screenshot.caption or screenshot.title or screenshot.image.name
            _write_line(lines, f"![{alt}]({path})")
            _write_line(lines)


def build_markdown_zip(machine):
    """
    Builds a ZIP containing the language-suffixed report plus copied screenshot assets.
    Returns (zip_bytes, filename).
    """
    machine_slug = slugify(machine.name) or f"machine-{machine.pk}"
    language_suffix = "es" if machine.report_language == "es" else "en"
    report_filename = f"{machine_slug}_{language_suffix}.md"
    i18n = get_i18n(machine.report_language)

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

        with translation.override(machine.report_language):
            lines = []
            _write_line(lines, f"# {machine.name}")
            _write_line(lines)
            
            if machine.report_type == 'ctf':
                _write_line(lines, f"- {i18n['platform']}: {machine.display_platform()}")
                _write_line(lines, f"- {i18n['difficulty']}: {machine.get_difficulty_display()}")
                _write_line(lines, f"- {i18n['operating_system']}: {machine.display_operating_system()}")
            else:
                if machine.client_name:
                    _write_line(lines, f"- {i18n.get('client', 'Client')}: {machine.client_name}")
                if machine.scope:
                    _write_line(lines, f"- {i18n.get('pt_scope', 'Scope')}: {machine.scope}")

            if machine.target_ip:
                _write_line(lines, f"- {i18n['target_ip']}: `{machine.target_ip}`")
            if machine.author:
                _write_line(lines, f"- {i18n.get('author_label', 'Author')}: {machine.author}")
            _write_line(lines)

            if machine.description:
                _section(lines, i18n['overview'])
                _write_line(lines, machine.description.strip())
                _write_line(lines)

            for phase_id, _ in Evidence.Phase.choices:
                if phase_id == Evidence.Phase.NOTES:
                    continue
                evidences = list(machine.evidences.filter(phase=phase_id))
                phase_vulns = list(machine.vulnerabilities.all()) if phase_id == Evidence.Phase.VULN_ID else []
                phase_exploits = list(machine.exploits.all()) if phase_id == Evidence.Phase.EXPLOIT else []
                if not evidences and not phase_vulns and not phase_exploits:
                    continue

                _section(lines, _phase_title(i18n, phase_id))

                for vuln in phase_vulns:
                    _write_line(lines, f"### {i18n['vulnerability']}: {vuln.title}")
                    _write_line(lines)
                    _write_line(lines, f"- {i18n['severity']}: {vuln.get_severity_display()}")
                    _write_line(lines, f"- {i18n['type']}: {vuln.display_vulnerability_type()}")
                    if vuln.cve:
                        _write_line(lines, f"- CVE: `{vuln.cve}`")
                    if vuln.affected_service or vuln.affected_port:
                        _write_line(lines, f"- {i18n['affected']}: {vuln.affected_service} {vuln.affected_port}".strip())
                    _write_line(lines)
                    if vuln.how_identified:
                        _write_line(lines, vuln.how_identified.strip())
                        _write_line(lines)
                    _code_block(lines, vuln.evidence)
                    if vuln.impact:
                        _write_line(lines, f"{i18n['impact']}: {vuln.impact.strip()}")
                        _write_line(lines)
                    if vuln.recommendation:
                        _write_line(lines, f"{i18n['recommendation']}: {vuln.recommendation.strip()}")
                        _write_line(lines)
                    _write_screenshots(lines, vuln.screenshots.all(), screenshot_paths)

                for exploit in phase_exploits:
                    _write_line(lines, f"### {i18n['exploit']}: {exploit.name}")
                    _write_line(lines)
                    _write_line(lines, f"- {i18n['type']}: {exploit.display_exploit_type()}")
                    _write_line(lines, f"- {i18n['objective']}: {exploit.get_objective_display()}")
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
                        _write_line(lines, f"{i18n['outcome']}: {exploit.result.strip()}")
                        _write_line(lines)
                    _write_screenshots(lines, exploit.screenshots.all(), screenshot_paths)

                for evidence in evidences:
                    _write_line(lines, f"### {evidence.title}")
                    _write_line(lines)
                    if evidence.explanation:
                        _write_line(lines, evidence.explanation.strip())
                        _write_line(lines)
                    _code_block(lines, evidence.command, "bash")
                    _code_block(lines, evidence.output)
                    _write_screenshots(lines, evidence.screenshots.all(), screenshot_paths)

            if machine.flags.exists():
                _section(lines, i18n['flags'])
                for flag in machine.flags.all():
                    _write_line(lines, f"### {flag.display_flag_type()}")
                    _write_line(lines)
                    value = i18n['censored'] if flag.censored else flag.value
                    _write_line(lines, f"- {i18n['value']}: `{value}`")
                    if flag.phase:
                        _write_line(lines, f"- {i18n['phase']}: {_phase_title(i18n, flag.phase)}")
                    if flag.location:
                        _write_line(lines, f"- {i18n['location']}: `{flag.location}`")
                    if flag.obtained_as_user:
                        _write_line(lines, f"- {i18n['user']}: `{flag.obtained_as_user}`")
                    _write_line(lines)
                    _code_block(lines, flag.found_commands, "bash")
                    if flag.notes:
                        _write_line(lines, flag.notes.strip())
                        _write_line(lines)

            notes = list(machine.evidences.filter(phase=Evidence.Phase.NOTES))
            if notes:
                _section(lines, i18n['notes'])
                for evidence in notes:
                    _write_line(lines, f"### {evidence.title}")
                    _write_line(lines)
                    if evidence.explanation:
                        _write_line(lines, evidence.explanation.strip())
                        _write_line(lines)
                    _code_block(lines, evidence.command, "bash")
                    _code_block(lines, evidence.output)
                    _write_screenshots(lines, evidence.screenshots.all(), screenshot_paths)

        report_path = os.path.join(tmp_dir, report_filename)
        with open(report_path, "w", encoding="utf-8") as report:
            report.write("\n".join(lines).rstrip() + "\n")

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for root, _, files in os.walk(tmp_dir):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    archive.write(full_path, os.path.relpath(full_path, tmp_dir))
        buffer.seek(0)

    return buffer.getvalue(), f"{machine_slug}_{language_suffix}-markdown.zip"
