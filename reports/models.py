from django.db import models
from django.utils.translation import gettext_lazy as _

class Machine(models.Model):
    class Platform(models.TextChoices):
        HTB = 'HackTheBox', _('HackTheBox')
        THM = 'TryHackMe', _('TryHackMe')
        VULNHUB = 'VulnHub', _('VulnHub')
        DOCKERLABS = 'DockerLabs', _('DockerLabs')
        OTHER = 'Other', _('Other')

    class Difficulty(models.TextChoices):
        EASY = 'Easy', _('Easy')
        MEDIUM = 'Medium', _('Medium')
        HARD = 'Hard', _('Hard')
        INSANE = 'Insane', _('Insane')
        UNKNOWN = 'Unknown', _('Unknown')

    class OS(models.TextChoices):
        LINUX = 'Linux', _('Linux')
        WINDOWS = 'Windows', _('Windows')
        FREEBSD = 'FreeBSD', _('FreeBSD')
        OTHER = 'Other', _('Other')
        UNKNOWN = 'Unknown', _('Unknown')

    class Status(models.TextChoices):
        IN_PROGRESS = 'In Progress', _('In Progress')
        COMPLETED = 'Completed', _('Completed')
        PAUSED = 'Paused', _('Paused')

    class Language(models.TextChoices):
        EN = 'en', _('English')
        ES = 'es', _('Español')

    class ReportType(models.TextChoices):
        CTF = 'ctf', _('CTF / HackTheBox / TryHackMe')
        BUG_BOUNTY = 'bug_bounty', _('Bug Bounty Report')
        PENTEST = 'pentest', _('Penetration Test (Corporate)')

    name = models.CharField(_("Name"), max_length=100)
    platform = models.CharField(_("Platform"), max_length=20, choices=Platform.choices, default=Platform.OTHER)
    custom_platform = models.CharField(_("Custom Platform"), max_length=100, blank=True)
    difficulty = models.CharField(_("Difficulty"), max_length=10, choices=Difficulty.choices, default=Difficulty.UNKNOWN)
    operating_system = models.CharField(_("Operating System"), max_length=10, choices=OS.choices, default=OS.UNKNOWN)
    custom_operating_system = models.CharField(_("Custom OS"), max_length=100, blank=True)
    target_ip = models.CharField(_("Target IP"), max_length=255, blank=True)
    author = models.CharField(_("Author"), max_length=100, blank=True)
    status = models.CharField(_("Status"), max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    report_language = models.CharField(_("Report Language"), max_length=2, choices=Language.choices, default=Language.ES)
    report_type = models.CharField(_("Report Type"), max_length=20, choices=ReportType.choices, default=ReportType.CTF)
    client_name = models.CharField(_("Client Name"), max_length=200, blank=True, help_text=_("Company/client name (for Pentest/Bug Bounty reports)"))
    scope = models.TextField(_("Scope"), blank=True, help_text=_("Scope of the engagement (URLs, IP ranges, etc.)"))
    description = models.TextField(_("Description"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.platform})"

class Evidence(models.Model):
    class Phase(models.TextChoices):
        RECON = 'reconnaissance', _('Reconnaissance')
        VULN_ID = 'vulnerability_identification', _('Vulnerability Identification')
        EXPLOIT = 'exploitation', _('Exploitation')
        INTERNAL_RECON = 'internal_reconnaissance', _('Internal Reconnaissance')
        USER_MOVEMENT = 'user_movement', _('User Movement')
        PRIVESC = 'privilege_escalation', _('Privilege Escalation')
        NOTES = 'notes', _('Notes')

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='evidences')
    phase = models.CharField(_("Phase"), max_length=50, choices=Phase.choices)
    title = models.CharField(_("Title"), max_length=200)
    command = models.TextField(_("Command"), blank=True)
    output = models.TextField(_("Output"), blank=True)
    explanation = models.TextField(_("Explanation"), blank=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['phase', 'order', 'created_at']

    def __str__(self):
        return f"[{self.get_phase_display()}] {self.title}"

class Vulnerability(models.Model):
    class Type(models.TextChoices):
        SQLI = 'SQL Injection', _('SQL Injection')
        XSS = 'XSS', _('XSS')
        LFI = 'LFI', _('LFI')
        RFI = 'RFI', _('RFI')
        SSRF = 'SSRF', _('SSRF')
        CMDI = 'Command Injection', _('Command Injection')
        FILE_UPLOAD = 'File Upload', _('File Upload')
        PATH_TRAVERSAL = 'Path Traversal', _('Path Traversal')
        WEAK_CREDS = 'Weak Credentials', _('Weak Credentials')
        EXPOSED_BACKUP = 'Exposed Backup', _('Exposed Backup')
        KERNEL = 'Kernel Exploit', _('Kernel Exploit')
        SUID = 'SUID Misconfiguration', _('SUID Misconfiguration')
        SUDO = 'Sudo Privileges', _('Sudo Privileges')
        MISCONFIG = 'Misconfigured Service', _('Misconfigured Service')
        CVE = 'Known CVE', _('Known CVE')
        OTHER = 'Other', _('Other')

    class Severity(models.TextChoices):
        INFO = 'Info', _('Info')
        LOW = 'Low', _('Low')
        MEDIUM = 'Medium', _('Medium')
        HIGH = 'High', _('High')
        CRITICAL = 'Critical', _('Critical')

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='vulnerabilities')
    title = models.CharField(_("Title"), max_length=200)
    affected_service = models.CharField(_("Affected Service"), max_length=200, blank=True)
    affected_port = models.CharField(_("Affected Port"), max_length=50, blank=True)
    vulnerability_type = models.CharField(_("Type"), max_length=50, choices=Type.choices)
    custom_vulnerability_type = models.CharField(_("Custom Type"), max_length=100, blank=True)
    severity = models.CharField(_("Severity"), max_length=20, choices=Severity.choices, default=Severity.INFO)
    cve = models.CharField(_("CVE"), max_length=50, blank=True)
    how_identified = models.TextField(_("How was it identified?"), blank=True)
    evidence = models.TextField(_("Evidence / Proof of Concept"), blank=True)
    impact = models.TextField(_("Technical Impact"), blank=True)
    recommendation = models.TextField(_("Remediation / Recommendation"), blank=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = 'Vulnerabilities'

    def __str__(self):
        return self.title

class Exploit(models.Model):
    class Type(models.TextChoices):
        MANUAL = 'Manual Technique', _('Manual Technique')
        CUSTOM = 'Custom Exploit', _('Custom Exploit')
        GITHUB = 'GitHub Repository', _('GitHub Repository')
        SEARCHSPLOIT = 'Searchsploit', _('Searchsploit')
        METASPLOIT = 'Metasploit Module', _('Metasploit Module')
        POC = 'Public PoC', _('Public PoC')
        OTHER = 'Other', _('Other')

    class Objective(models.TextChoices):
        INITIAL_ACCESS = 'Initial Access', _('Initial Access')
        RCE = 'Remote Code Execution', _('Remote Code Execution')
        CREDS = 'Credential Disclosure', _('Credential Disclosure')
        PIVOT = 'User Pivot', _('User Pivot')
        PRIVESC = 'Privilege Escalation', _('Privilege Escalation')
        POC = 'Proof of Concept', _('Proof of Concept')

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='exploits')
    vulnerability = models.ForeignKey(Vulnerability, on_delete=models.SET_NULL, null=True, blank=True, related_name='exploits', verbose_name=_("Vulnerability"))
    name = models.CharField(_("Name"), max_length=200)
    exploit_type = models.CharField(_("Type"), max_length=50, choices=Type.choices)
    custom_exploit_type = models.CharField(_("Custom Type"), max_length=100, blank=True)
    cve = models.CharField(_("CVE"), max_length=50, blank=True)
    url = models.URLField(_("URL"), blank=True)
    local_path = models.CharField(_("Local Path"), max_length=255, blank=True)
    affected_service = models.CharField(_("Affected Service"), max_length=200, blank=True)
    affected_port = models.CharField(_("Affected Port"), max_length=50, blank=True)
    objective = models.CharField(_("Objective"), max_length=50, choices=Objective.choices)
    command_used = models.TextField(_("Command Used"), blank=True)
    output = models.TextField(_("Output"), blank=True)
    result = models.TextField(_("Result"), blank=True)
    explanation = models.TextField(_("Explanation"), blank=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.name

def screenshot_upload_path(instance, filename):
    from slugify import slugify
    machine_slug = slugify(instance.machine.name)
    return f'screenshots/{machine_slug}/{filename}'

class Screenshot(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='screenshots')
    evidence = models.ForeignKey(Evidence, on_delete=models.SET_NULL, null=True, blank=True, related_name='screenshots')
    vulnerability = models.ForeignKey(Vulnerability, on_delete=models.SET_NULL, null=True, blank=True, related_name='screenshots')
    exploit = models.ForeignKey(Exploit, on_delete=models.SET_NULL, null=True, blank=True, related_name='screenshots')
    phase = models.CharField(max_length=50, choices=Evidence.Phase.choices, blank=True)
    image = models.ImageField(upload_to=screenshot_upload_path)
    title = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Screenshot: {self.title or self.image.name}"

class Flag(models.Model):
    class Type(models.TextChoices):
        USER = 'user.txt', _('user.txt')
        ROOT = 'root.txt', _('root.txt')
        LOCAL = 'local.txt', _('local.txt')
        PROOF = 'proof.txt', _('proof.txt')
        OTHER = 'other', _('other')

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='flags')
    flag_type = models.CharField(_("Flag Type"), max_length=20, choices=Type.choices)
    custom_flag_type = models.CharField(_("Custom Type"), max_length=100, blank=True)
    phase = models.CharField(_("Phase"), max_length=50, choices=Evidence.Phase.choices, blank=True, help_text=_('Phase where the flag was found'))
    value = models.CharField(_("Value"), max_length=255)
    location = models.CharField(_("Location / Path"), max_length=255, blank=True)
    obtained_as_user = models.CharField(_("Obtained as User"), max_length=100, blank=True)
    found_commands = models.TextField(_("Command(s) Used"), blank=True, help_text=_('Commands used to obtain this flag'))
    notes = models.TextField(_("Additional Notes"), blank=True)
    censored = models.BooleanField(_("Censor in Report"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.flag_type} ({self.machine.name})"

