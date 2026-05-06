import zipfile
from io import BytesIO
from tempfile import TemporaryDirectory

from django.test import TestCase, override_settings

from reports.models import Machine, Evidence, Vulnerability, Exploit, Flag
from reports.services.latex_renderer import render_machine_to_latex
from reports.services.markdown_exporter import build_markdown_zip


class MarkdownExportTest(TestCase):
    """Tests for the Markdown ZIP exporter."""

    def _create_full_machine(self, name="TestBox", language="en"):
        """Helper to build a machine with evidences, vulns, exploits and flags."""
        machine = Machine.objects.create(
            name=name,
            platform=Machine.Platform.HTB,
            difficulty=Machine.Difficulty.MEDIUM,
            operating_system=Machine.OS.LINUX,
            target_ip="10.10.10.1",
            author="tester",
            report_language=language,
            report_type=Machine.ReportType.CTF,
            description="A test machine for export verification.",
        )
        Evidence.objects.create(
            machine=machine,
            phase=Evidence.Phase.RECON,
            title="Port Scan",
            command="nmap -sV 10.10.10.1",
            output="22/tcp open ssh\n80/tcp open http",
            explanation="Initial port enumeration.",
            order=1,
        )
        Evidence.objects.create(
            machine=machine,
            phase=Evidence.Phase.PRIVESC,
            title="Sudo Enumeration",
            command="sudo -l",
            output="(ALL) NOPASSWD: /usr/bin/vim",
            explanation="User can run vim as root.",
            order=1,
        )
        Vulnerability.objects.create(
            machine=machine,
            title="Weak SSH Credentials",
            vulnerability_type=Vulnerability.Type.WEAK_CREDS,
            severity=Vulnerability.Severity.HIGH,
            how_identified="Brute force with hydra.",
            evidence="hydra -l admin -P rockyou.txt ssh://10.10.10.1",
            impact="Full access to the system via SSH.",
            recommendation="Use strong passwords and disable password-based auth.",
        )
        Exploit.objects.create(
            machine=machine,
            name="SSH Login",
            exploit_type=Exploit.Type.MANUAL,
            objective=Exploit.Objective.INITIAL_ACCESS,
            command_used="ssh admin@10.10.10.1",
            output="Welcome to Ubuntu",
            result="Got initial shell as admin.",
        )
        Flag.objects.create(
            machine=machine,
            flag_type=Flag.Type.USER,
            value="abc123def456",
            location="/home/admin/user.txt",
            obtained_as_user="admin",
            phase=Evidence.Phase.EXPLOIT,
            censored=True,
        )
        Flag.objects.create(
            machine=machine,
            flag_type=Flag.Type.ROOT,
            value="root_hash_789",
            location="/root/root.txt",
            obtained_as_user="root",
            phase=Evidence.Phase.PRIVESC,
            censored=False,
        )
        return machine

    def test_empty_machine_exports_valid_zip(self):
        machine = Machine.objects.create(name="EmptyBox")
        archive_bytes, filename = build_markdown_zip(machine)
        self.assertTrue(filename.endswith(".zip"))
        self.assertIn("emptybox", filename)

        with zipfile.ZipFile(BytesIO(archive_bytes)) as zf:
            names = zf.namelist()
            # Should contain at least the markdown file
            md_files = [n for n in names if n.endswith(".md")]
            self.assertEqual(len(md_files), 1)

    def test_english_export_filename_suffix(self):
        machine = Machine.objects.create(name="LangBox", report_language="en")
        _, filename = build_markdown_zip(machine)
        self.assertIn("_en", filename)

    def test_spanish_export_filename_suffix(self):
        machine = Machine.objects.create(name="LangBox", report_language="es")
        _, filename = build_markdown_zip(machine)
        self.assertIn("_es", filename)

    def test_full_machine_markdown_content(self):
        machine = self._create_full_machine(language="en")
        archive_bytes, filename = build_markdown_zip(machine)

        with zipfile.ZipFile(BytesIO(archive_bytes)) as zf:
            md_files = [n for n in zf.namelist() if n.endswith(".md")]
            self.assertEqual(len(md_files), 1)

            content = zf.read(md_files[0]).decode("utf-8")

            # Machine header
            self.assertIn("# TestBox", content)
            self.assertIn("HackTheBox", content)
            self.assertIn("10.10.10.1", content)

            # Description / Overview
            self.assertIn("test machine for export verification", content)

            # Reconnaissance evidence
            self.assertIn("Port Scan", content)
            self.assertIn("nmap -sV", content)

            # Vulnerability
            self.assertIn("Weak SSH Credentials", content)
            self.assertIn("High", content)

            # Exploit
            self.assertIn("SSH Login", content)
            self.assertIn("Initial Access", content)

            # Flags
            self.assertIn("user.txt", content)
            self.assertIn("[CENSORED]", content)
            # Uncensored root flag
            self.assertIn("root_hash_789", content)

    def test_full_machine_spanish_content(self):
        machine = self._create_full_machine(name="CajaTest", language="es")
        archive_bytes, _ = build_markdown_zip(machine)

        with zipfile.ZipFile(BytesIO(archive_bytes)) as zf:
            md_files = [n for n in zf.namelist() if n.endswith(".md")]
            content = zf.read(md_files[0]).decode("utf-8")

            # Spanish i18n strings
            self.assertIn("Plataforma", content)
            self.assertIn("Dificultad", content)
            self.assertIn("Reconocimiento", content)
            self.assertIn("Vulnerabilidad", content)

    def test_spanish_markdown_export_translates_choice_values(self):
        machine = Machine.objects.create(
            name="CajaOpciones",
            platform=Machine.Platform.OTHER,
            custom_platform="PortSwigger Academy",
            difficulty=Machine.Difficulty.EASY,
            operating_system=Machine.OS.OTHER,
            custom_operating_system="TempleOS",
            report_language="es",
        )
        Vulnerability.objects.create(
            machine=machine,
            title="Finding",
            vulnerability_type=Vulnerability.Type.OTHER,
            custom_vulnerability_type="Race Condition",
            severity=Vulnerability.Severity.HIGH,
        )
        Exploit.objects.create(
            machine=machine,
            name="Manual Exploit",
            exploit_type=Exploit.Type.OTHER,
            custom_exploit_type="One-off Script",
            objective=Exploit.Objective.INITIAL_ACCESS,
        )
        Flag.objects.create(
            machine=machine,
            flag_type=Flag.Type.OTHER,
            custom_flag_type="bonus.txt",
            value="secret",
            censored=True,
        )

        archive_bytes, _ = build_markdown_zip(machine)

        with zipfile.ZipFile(BytesIO(archive_bytes)) as zf:
            md_files = [n for n in zf.namelist() if n.endswith(".md")]
            content = zf.read(md_files[0]).decode("utf-8")

            self.assertIn("Plataforma: PortSwigger Academy", content)
            self.assertIn("Dificultad: Fácil", content)
            self.assertIn("Sistema Operativo: TempleOS", content)
            self.assertIn("Severidad: Alto", content)
            self.assertIn("Tipo: Race Condition", content)
            self.assertIn("Tipo: One-off Script", content)
            self.assertIn("Objetivo: Acceso Inicial", content)
            self.assertIn("### bonus.txt", content)
            self.assertIn("[CENSURADO]", content)
            self.assertNotIn("Plataforma: Otro", content)
            self.assertNotIn("Sistema Operativo: Otro", content)
            self.assertNotIn("Platform: Other", content)
            self.assertNotIn("Difficulty: Easy", content)
            self.assertNotIn("[censored]", content)

    def test_professional_markdown_uses_client_scope_instead_of_ctf_fields(self):
        machine = Machine.objects.create(
            name="ProfessionalTarget",
            platform=Machine.Platform.HTB,
            difficulty=Machine.Difficulty.HARD,
            operating_system=Machine.OS.LINUX,
            target_ip="203.0.113.10",
            author="Consultant",
            report_language="en",
            report_type=Machine.ReportType.PENTEST,
            client_name="Acme Corp",
            scope="api.acme.test, 203.0.113.0/24",
        )

        archive_bytes, _ = build_markdown_zip(machine)

        with zipfile.ZipFile(BytesIO(archive_bytes)) as zf:
            md_files = [n for n in zf.namelist() if n.endswith(".md")]
            content = zf.read(md_files[0]).decode("utf-8")

            self.assertIn("Client: Acme Corp", content)
            self.assertIn("Scope of Work: api.acme.test, 203.0.113.0/24", content)
            self.assertIn("Target IP: `203.0.113.10`", content)
            self.assertIn("Author: Consultant", content)
            self.assertNotIn("Platform:", content)
            self.assertNotIn("Difficulty:", content)
            self.assertNotIn("Operating System:", content)
            self.assertNotIn("HackTheBox", content)
            self.assertNotIn("Hard", content)
            self.assertNotIn("Linux", content)

    def test_spanish_latex_export_translates_choice_values(self):
        with TemporaryDirectory() as export_root:
            with override_settings(EXPORTS_ROOT=export_root):
                machine = Machine.objects.create(
                    name="CajaLatex",
                    platform=Machine.Platform.OTHER,
                    custom_platform="PortSwigger Academy",
                    difficulty=Machine.Difficulty.EASY,
                    operating_system=Machine.OS.OTHER,
                    custom_operating_system="TempleOS",
                    report_language="es",
                )
                Vulnerability.objects.create(
                    machine=machine,
                    title="Finding",
                    vulnerability_type=Vulnerability.Type.OTHER,
                    custom_vulnerability_type="Race Condition",
                    severity=Vulnerability.Severity.HIGH,
                )
                Exploit.objects.create(
                    machine=machine,
                    name="Manual Exploit",
                    exploit_type=Exploit.Type.OTHER,
                    custom_exploit_type="One-off Script",
                    objective=Exploit.Objective.INITIAL_ACCESS,
                )
                Flag.objects.create(
                    machine=machine,
                    flag_type=Flag.Type.OTHER,
                    custom_flag_type="bonus.txt",
                    value="secret",
                    censored=True,
                )

                _, tex_path = render_machine_to_latex(machine)

                with open(tex_path, encoding="utf-8") as report:
                    content = report.read()

            self.assertIn("PortSwigger Academy", content)
            self.assertIn("TempleOS", content)
            self.assertIn("Fácil", content)
            self.assertIn("Alto", content)
            self.assertIn("Race Condition", content)
            self.assertIn("One-off Script", content)
            self.assertIn("bonus.txt", content)
            self.assertIn("Acceso Inicial", content)
            self.assertIn("[CENSURADO]", content)
            self.assertNotIn("Other", content)
            self.assertNotIn("Otro", content)
            self.assertNotIn("Easy", content)
            self.assertNotIn("Initial Access", content)

    def test_pentest_latex_uses_client_scope_instead_of_ctf_fields(self):
        with TemporaryDirectory() as export_root:
            with override_settings(EXPORTS_ROOT=export_root):
                machine = Machine.objects.create(
                    name="PentestTarget",
                    platform=Machine.Platform.HTB,
                    difficulty=Machine.Difficulty.HARD,
                    operating_system=Machine.OS.LINUX,
                    target_ip="203.0.113.10",
                    author="Consultant",
                    report_language="en",
                    report_type=Machine.ReportType.PENTEST,
                    client_name="Acme Corp",
                    scope="api.acme.test, 203.0.113.0/24",
                )

                _, tex_path = render_machine_to_latex(machine)

                with open(tex_path, encoding="utf-8") as report:
                    content = report.read()

            self.assertIn("Acme Corp", content)
            self.assertIn("Scope of Work", content)
            self.assertIn("api.acme.test, 203.0.113.0/24", content)
            self.assertIn("203.0.113.10", content)
            self.assertIn("Consultant", content)
            self.assertNotIn("Platform", content)
            self.assertNotIn("Difficulty", content)
            self.assertNotIn("HackTheBox", content)
            self.assertNotIn("Hard", content)
            self.assertNotIn("Linux", content)

    def test_bug_bounty_latex_uses_client_scope_instead_of_ctf_fields(self):
        with TemporaryDirectory() as export_root:
            with override_settings(EXPORTS_ROOT=export_root):
                machine = Machine.objects.create(
                    name="BugTarget",
                    platform=Machine.Platform.HTB,
                    difficulty=Machine.Difficulty.MEDIUM,
                    operating_system=Machine.OS.WINDOWS,
                    target_ip="198.51.100.25",
                    author="Researcher",
                    report_language="en",
                    report_type=Machine.ReportType.BUG_BOUNTY,
                    client_name="Acme Web",
                    scope="https://app.acme.test",
                )

                _, tex_path = render_machine_to_latex(machine)

                with open(tex_path, encoding="utf-8") as report:
                    content = report.read()

            self.assertIn("Acme Web", content)
            self.assertIn("Scope of Work", content)
            self.assertIn("https://app.acme.test", content)
            self.assertIn("198.51.100.25", content)
            self.assertIn("Researcher", content)
            self.assertNotIn("Platform", content)
            self.assertNotIn("Difficulty", content)
            self.assertNotIn("HackTheBox", content)
            self.assertNotIn("Medium", content)
            self.assertNotIn("Windows", content)

    def test_notes_phase_at_end(self):
        machine = Machine.objects.create(name="NotesBox")
        Evidence.objects.create(
            machine=machine,
            phase=Evidence.Phase.NOTES,
            title="Important Note",
            explanation="Remember to check cron jobs.",
        )
        archive_bytes, _ = build_markdown_zip(machine)

        with zipfile.ZipFile(BytesIO(archive_bytes)) as zf:
            md_files = [n for n in zf.namelist() if n.endswith(".md")]
            content = zf.read(md_files[0]).decode("utf-8")
            self.assertIn("Important Note", content)
            self.assertIn("cron jobs", content)
