import zipfile
from io import BytesIO

from django.test import TestCase

from reports.models import Machine, Evidence, Vulnerability, Exploit, Flag
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
            self.assertIn("[censored]", content)
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
