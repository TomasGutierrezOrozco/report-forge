from django.test import TestCase, Client
from django.urls import reverse

from reports.models import Machine, Evidence, Vulnerability, Exploit, Flag


class MachineViewsTest(TestCase):
    """Tests for machine CRUD views."""

    def setUp(self):
        self.client = Client()
        self.machine = Machine.objects.create(
            name="ViewTestBox",
            platform=Machine.Platform.HTB,
            difficulty=Machine.Difficulty.EASY,
        )

    def test_machine_list_view(self):
        response = self.client.get(reverse("reports:machine_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ViewTestBox")

    def test_machine_detail_view(self):
        response = self.client.get(
            reverse("reports:machine_detail", args=[self.machine.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ViewTestBox")

    def test_machine_create_view_get(self):
        response = self.client.get(reverse("reports:machine_create"))
        self.assertEqual(response.status_code, 200)

    def test_machine_create_view_post(self):
        response = self.client.post(
            reverse("reports:machine_create"),
            {
                "name": "NewMachine",
                "platform": "HackTheBox",
                "difficulty": "Medium",
                "operating_system": "Linux",
                "status": "In Progress",
                "report_language": "en",
                "report_type": "ctf",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Machine.objects.filter(name="NewMachine").exists())

    def test_machine_edit_view(self):
        response = self.client.post(
            reverse("reports:machine_edit", args=[self.machine.pk]),
            {
                "name": "UpdatedBox",
                "platform": "HackTheBox",
                "difficulty": "Hard",
                "operating_system": "Linux",
                "status": "Completed",
                "report_language": "es",
                "report_type": "ctf",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.machine.refresh_from_db()
        self.assertEqual(self.machine.name, "UpdatedBox")
        self.assertEqual(self.machine.difficulty, "Hard")

    def test_machine_delete_view(self):
        pk = self.machine.pk
        response = self.client.post(
            reverse("reports:machine_delete", args=[pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Machine.objects.filter(pk=pk).exists())

    def test_nonexistent_machine_returns_404(self):
        response = self.client.get(
            reverse("reports:machine_detail", args=[99999])
        )
        self.assertEqual(response.status_code, 404)


class EvidenceViewsTest(TestCase):
    """Tests for evidence CRUD views."""

    def setUp(self):
        self.client = Client()
        self.machine = Machine.objects.create(name="EvidenceBox")

    def test_evidence_create_get(self):
        response = self.client.get(
            reverse("reports:evidence_create", args=[self.machine.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_evidence_create_post(self):
        response = self.client.post(
            reverse("reports:evidence_create", args=[self.machine.pk]),
            {
                "phase": "reconnaissance",
                "title": "Test Evidence",
                "command": "whoami",
                "output": "root",
                "explanation": "Check current user",
                "order": 1,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.machine.evidences.count(), 1)


class ExportViewsTest(TestCase):
    """Tests for export views."""

    def setUp(self):
        self.client = Client()
        self.machine = Machine.objects.create(
            name="ExportBox",
            report_language="en",
            report_type="ctf",
        )

    def test_export_view_get(self):
        response = self.client.get(
            reverse("reports:export_view", args=[self.machine.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_export_markdown_returns_zip(self):
        response = self.client.get(
            reverse("reports:export_markdown", args=[self.machine.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertIn("exportbox", response["Content-Disposition"])

    def test_export_latex_redirect(self):
        response = self.client.get(
            reverse("reports:export_latex", args=[self.machine.pk])
        )
        self.assertEqual(response.status_code, 302)


class ReorderViewTest(TestCase):
    """Tests for the reorder endpoint."""

    def setUp(self):
        self.client = Client()
        self.machine = Machine.objects.create(name="ReorderBox")
        self.ev1 = Evidence.objects.create(
            machine=self.machine, phase=Evidence.Phase.RECON, title="A", order=1
        )
        self.ev2 = Evidence.objects.create(
            machine=self.machine, phase=Evidence.Phase.RECON, title="B", order=2
        )

    def test_reorder_evidence(self):
        import json

        response = self.client.post(
            reverse("reports:reorder_items", args=[self.machine.pk]),
            data=json.dumps({"type": "evidence", "ids": [self.ev2.pk, self.ev1.pk]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.ev1.refresh_from_db()
        self.ev2.refresh_from_db()
        self.assertEqual(self.ev2.order, 1)
        self.assertEqual(self.ev1.order, 2)

    def test_reorder_invalid_type(self):
        import json

        response = self.client.post(
            reverse("reports:reorder_items", args=[self.machine.pk]),
            data=json.dumps({"type": "invalid", "ids": [1]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_reorder_invalid_json(self):
        response = self.client.post(
            reverse("reports:reorder_items", args=[self.machine.pk]),
            data="not json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
