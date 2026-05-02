from django.db import models

class Machine(models.Model):
    class Platform(models.TextChoices):
        HTB = 'HackTheBox', 'HackTheBox'
        THM = 'TryHackMe', 'TryHackMe'
        VULNHUB = 'VulnHub', 'VulnHub'
        DOCKERLABS = 'DockerLabs', 'DockerLabs'
        OTHER = 'Other', 'Other'

    class Difficulty(models.TextChoices):
        EASY = 'Easy', 'Easy'
        MEDIUM = 'Medium', 'Medium'
        HARD = 'Hard', 'Hard'
        INSANE = 'Insane', 'Insane'
        UNKNOWN = 'Unknown', 'Unknown'

    class OS(models.TextChoices):
        LINUX = 'Linux', 'Linux'
        WINDOWS = 'Windows', 'Windows'
        FREEBSD = 'FreeBSD', 'FreeBSD'
        OTHER = 'Other', 'Other'
        UNKNOWN = 'Unknown', 'Unknown'

    class Status(models.TextChoices):
        IN_PROGRESS = 'In Progress', 'In Progress'
        COMPLETED = 'Completed', 'Completed'
        PAUSED = 'Paused', 'Paused'

    class Language(models.TextChoices):
        EN = 'en', 'English'
        ES = 'es', 'Español'

    class ReportType(models.TextChoices):
        CTF = 'ctf', 'CTF / HackTheBox / TryHackMe'
        BUG_BOUNTY = 'bug_bounty', 'Bug Bounty Report'
        PENTEST = 'pentest', 'Penetration Test (Corporate)'

    name = models.CharField(max_length=100)
    platform = models.CharField(max_length=20, choices=Platform.choices, default=Platform.OTHER)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.UNKNOWN)
    operating_system = models.CharField(max_length=10, choices=OS.choices, default=OS.UNKNOWN)
    target_ip = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    report_language = models.CharField(max_length=2, choices=Language.choices, default=Language.ES)
    report_type = models.CharField(max_length=20, choices=ReportType.choices, default=ReportType.CTF)
    # Extra fields for non-CTF reports
    client_name = models.CharField(max_length=200, blank=True, help_text="Company/client name (for Pentest/Bug Bounty reports)")
    scope = models.TextField(blank=True, help_text="Scope of the engagement (URLs, IP ranges, etc.)")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.platform})"

class Evidence(models.Model):
    class Phase(models.TextChoices):
        RECON = 'reconnaissance', 'Reconnaissance'
        VULN_ID = 'vulnerability_identification', 'Vulnerability Identification'
        EXPLOIT = 'exploitation', 'Exploitation'
        INTERNAL_RECON = 'internal_reconnaissance', 'Internal Reconnaissance'
        USER_MOVEMENT = 'user_movement', 'User Movement'
        PRIVESC = 'privilege_escalation', 'Privilege Escalation'
        NOTES = 'notes', 'Notes'

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='evidences')
    phase = models.CharField(max_length=50, choices=Phase.choices)
    title = models.CharField(max_length=200)
    command = models.TextField(blank=True)
    output = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['phase', 'order', 'created_at']

    def __str__(self):
        return f"[{self.get_phase_display()}] {self.title}"

class Vulnerability(models.Model):
    class Type(models.TextChoices):
        SQLI = 'SQL Injection', 'SQL Injection'
        XSS = 'XSS', 'XSS'
        LFI = 'LFI', 'LFI'
        RFI = 'RFI', 'RFI'
        SSRF = 'SSRF', 'SSRF'
        CMDI = 'Command Injection', 'Command Injection'
        FILE_UPLOAD = 'File Upload', 'File Upload'
        PATH_TRAVERSAL = 'Path Traversal', 'Path Traversal'
        WEAK_CREDS = 'Weak Credentials', 'Weak Credentials'
        EXPOSED_BACKUP = 'Exposed Backup', 'Exposed Backup'
        KERNEL = 'Kernel Exploit', 'Kernel Exploit'
        SUID = 'SUID Misconfiguration', 'SUID Misconfiguration'
        SUDO = 'Sudo Privileges', 'Sudo Privileges'
        MISCONFIG = 'Misconfigured Service', 'Misconfigured Service'
        CVE = 'Known CVE', 'Known CVE'
        OTHER = 'Other', 'Other'

    class Severity(models.TextChoices):
        INFO = 'Info', 'Info'
        LOW = 'Low', 'Low'
        MEDIUM = 'Medium', 'Medium'
        HIGH = 'High', 'High'
        CRITICAL = 'Critical', 'Critical'

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='vulnerabilities')
    title = models.CharField(max_length=200)
    affected_service = models.CharField(max_length=200, blank=True)
    affected_port = models.CharField(max_length=50, blank=True)
    vulnerability_type = models.CharField(max_length=50, choices=Type.choices)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.INFO)
    cve = models.CharField(max_length=50, blank=True)
    how_identified = models.TextField(blank=True)
    evidence = models.TextField(blank=True)
    impact = models.TextField(blank=True)
    recommendation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = 'Vulnerabilities'

    def __str__(self):
        return self.title

class Exploit(models.Model):
    class Type(models.TextChoices):
        MANUAL = 'Manual Technique', 'Manual Technique'
        CUSTOM = 'Custom Exploit', 'Custom Exploit'
        GITHUB = 'GitHub Repository', 'GitHub Repository'
        SEARCHSPLOIT = 'Searchsploit', 'Searchsploit'
        METASPLOIT = 'Metasploit Module', 'Metasploit Module'
        POC = 'Public PoC', 'Public PoC'
        OTHER = 'Other', 'Other'

    class Objective(models.TextChoices):
        INITIAL_ACCESS = 'Initial Access', 'Initial Access'
        RCE = 'Remote Code Execution', 'Remote Code Execution'
        CREDS = 'Credential Disclosure', 'Credential Disclosure'
        PIVOT = 'User Pivot', 'User Pivot'
        PRIVESC = 'Privilege Escalation', 'Privilege Escalation'
        POC = 'Proof of Concept', 'Proof of Concept'

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='exploits')
    vulnerability = models.ForeignKey(Vulnerability, on_delete=models.SET_NULL, null=True, blank=True, related_name='exploits')
    name = models.CharField(max_length=200)
    exploit_type = models.CharField(max_length=50, choices=Type.choices)
    cve = models.CharField(max_length=50, blank=True)
    url = models.URLField(blank=True)
    local_path = models.CharField(max_length=255, blank=True)
    affected_service = models.CharField(max_length=200, blank=True)
    affected_port = models.CharField(max_length=50, blank=True)
    objective = models.CharField(max_length=50, choices=Objective.choices)
    command_used = models.TextField(blank=True)
    output = models.TextField(blank=True)
    result = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
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
        USER = 'user.txt', 'user.txt'
        ROOT = 'root.txt', 'root.txt'
        LOCAL = 'local.txt', 'local.txt'
        PROOF = 'proof.txt', 'proof.txt'
        OTHER = 'other', 'other'

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='flags')
    flag_type = models.CharField(max_length=20, choices=Type.choices)
    phase = models.CharField(max_length=50, choices=Evidence.Phase.choices, blank=True, help_text='Phase where the flag was found')
    value = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    obtained_as_user = models.CharField(max_length=100, blank=True)
    found_commands = models.TextField(blank=True, help_text='Commands used to obtain this flag')
    notes = models.TextField(blank=True)
    censored = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.flag_type} ({self.machine.name})"

