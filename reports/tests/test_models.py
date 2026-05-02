from django.test import TestCase

from reports.models import Machine, Evidence, Vulnerability, Exploit, Flag, Screenshot


class MachineModelTest(TestCase):
    """Tests for the Machine model defaults and basic behavior."""

    def test_create_machine_with_defaults(self):
        machine = Machine.objects.create(name="TestBox")
        self.assertEqual(machine.platform, Machine.Platform.OTHER)
        self.assertEqual(machine.difficulty, Machine.Difficulty.UNKNOWN)
        self.assertEqual(machine.operating_system, Machine.OS.UNKNOWN)
        self.assertEqual(machine.status, Machine.Status.IN_PROGRESS)
        self.assertEqual(machine.report_language, Machine.Language.ES)
        self.assertEqual(machine.report_type, Machine.ReportType.CTF)

    def test_machine_str(self):
        machine = Machine.objects.create(name="Lame", platform=Machine.Platform.HTB)
        self.assertEqual(str(machine), "Lame (HackTheBox)")

    def test_machine_timestamps(self):
        machine = Machine.objects.create(name="TimedBox")
        self.assertIsNotNone(machine.created_at)
        self.assertIsNotNone(machine.updated_at)


class EvidenceModelTest(TestCase):
    """Tests for the Evidence model."""

    def setUp(self):
        self.machine = Machine.objects.create(name="TestBox")

    def test_create_evidence(self):
        evidence = Evidence.objects.create(
            machine=self.machine,
            phase=Evidence.Phase.RECON,
            title="Nmap Scan",
            command="nmap -sV 10.10.10.1",
            output="22/tcp open ssh",
            order=1,
        )
        self.assertEqual(evidence.machine, self.machine)
        self.assertEqual(evidence.phase, "reconnaissance")
        self.assertIn("Reconnaissance", str(evidence))

    def test_evidence_ordering(self):
        Evidence.objects.create(
            machine=self.machine, phase=Evidence.Phase.RECON, title="Second", order=2
        )
        Evidence.objects.create(
            machine=self.machine, phase=Evidence.Phase.RECON, title="First", order=1
        )
        evidences = list(self.machine.evidences.all())
        self.assertEqual(evidences[0].title, "First")
        self.assertEqual(evidences[1].title, "Second")

    def test_cascade_delete(self):
        Evidence.objects.create(
            machine=self.machine, phase=Evidence.Phase.RECON, title="To Delete"
        )
        self.assertEqual(Evidence.objects.count(), 1)
        self.machine.delete()
        self.assertEqual(Evidence.objects.count(), 0)


class VulnerabilityModelTest(TestCase):
    """Tests for the Vulnerability model."""

    def setUp(self):
        self.machine = Machine.objects.create(name="VulnBox")

    def test_create_vulnerability(self):
        vuln = Vulnerability.objects.create(
            machine=self.machine,
            title="SQL Injection in Login",
            vulnerability_type=Vulnerability.Type.SQLI,
            severity=Vulnerability.Severity.HIGH,
            cve="CVE-2024-1234",
        )
        self.assertEqual(vuln.severity, "High")
        self.assertEqual(str(vuln), "SQL Injection in Login")

    def test_vulnerability_ordering(self):
        Vulnerability.objects.create(
            machine=self.machine,
            title="Second",
            vulnerability_type=Vulnerability.Type.XSS,
            order=2,
        )
        Vulnerability.objects.create(
            machine=self.machine,
            title="First",
            vulnerability_type=Vulnerability.Type.SQLI,
            order=1,
        )
        vulns = list(self.machine.vulnerabilities.all())
        self.assertEqual(vulns[0].title, "First")
        self.assertEqual(vulns[1].title, "Second")


class ExploitModelTest(TestCase):
    """Tests for the Exploit model."""

    def setUp(self):
        self.machine = Machine.objects.create(name="ExploitBox")

    def test_create_exploit(self):
        exploit = Exploit.objects.create(
            machine=self.machine,
            name="Manual SQLi",
            exploit_type=Exploit.Type.MANUAL,
            objective=Exploit.Objective.INITIAL_ACCESS,
            command_used="sqlmap -u http://target/login",
        )
        self.assertEqual(str(exploit), "Manual SQLi")
        self.assertEqual(exploit.objective, "Initial Access")

    def test_exploit_with_vulnerability(self):
        vuln = Vulnerability.objects.create(
            machine=self.machine,
            title="SQLi",
            vulnerability_type=Vulnerability.Type.SQLI,
        )
        exploit = Exploit.objects.create(
            machine=self.machine,
            name="SQLi Exploit",
            vulnerability=vuln,
            exploit_type=Exploit.Type.MANUAL,
            objective=Exploit.Objective.RCE,
        )
        self.assertEqual(exploit.vulnerability, vuln)
        # Deleting vuln should SET_NULL on exploit
        vuln.delete()
        exploit.refresh_from_db()
        self.assertIsNone(exploit.vulnerability)


class FlagModelTest(TestCase):
    """Tests for the Flag model."""

    def setUp(self):
        self.machine = Machine.objects.create(name="FlagBox")

    def test_create_flag(self):
        flag = Flag.objects.create(
            machine=self.machine,
            flag_type=Flag.Type.USER,
            value="abc123",
            location="/home/user/user.txt",
            obtained_as_user="www-data",
            censored=True,
        )
        self.assertTrue(flag.censored)
        self.assertIn("user.txt", str(flag))

    def test_flag_defaults(self):
        flag = Flag.objects.create(
            machine=self.machine,
            flag_type=Flag.Type.ROOT,
            value="root_hash",
        )
        self.assertTrue(flag.censored)
        self.assertEqual(flag.phase, "")
