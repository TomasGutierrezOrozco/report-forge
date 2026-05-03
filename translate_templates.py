import os
import re

template_dir = 'reports/templates/reports'

# Regex to find <label ...>Text</label>
label_re = re.compile(r'(<label[^>]*>)([^<]+)(</label>)')

# Regex to find help text in <div class="form-text...">Text</div>
help_re = re.compile(r'(<div[^>]*class="[^"]*form-text[^"]*"[^>]*>)([^<]+)(</div>)')

# Regex to find <h4>Text</h4>
h4_re = re.compile(r'(<h4[^>]*>)([^<]+)(</h4>)')

# Regex to find <button ...>Text</button>
button_re = re.compile(r'(<button[^>]*>)([^<]+)(</button>)')

for filename in os.listdir(template_dir):
    if not filename.endswith('_form.html') and filename != 'machine_detail.html':
        continue
        
    path = os.path.join(template_dir, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    def repl(m):
        prefix, text, suffix = m.groups()
        # Clean text
        inner = text.strip()
        if not inner or '{%' in inner or '{{' in inner or 'trans' in inner:
            return m.group(0)
            
        # Strip some things like <span class="text-danger">*</span> if they were matched (they won't be matched by [^<]+ though)
        return f'{prefix}{{% trans "{inner}" %}}{suffix}'
        
    # Replace labels but carefully:
    # labels can have inner HTML like <span>. So we only match if it's pure text.
    # Actually, many labels have <span class="text-danger">*</span> which means [^<]+ won't match the whole label.
    # Let's do a more generic replacement.
    
    # We will manually replace common strings
    common_strings = [
        "Target Name", "Target IP", "Configure the workspace for this engagement.",
        "Target Service", "Target Port", "Command Executed", "Result / Outcome", "Timeline Order",
        "Found During", "Censor in Report", "Flag Value / Hash", 
        "Enter the exact flag value. It will be hidden if \"Censor in Report\" is checked.",
        "Location / Path", "e.g., C:\\Users\\Administrator\\Desktop\\root.txt",
        "Obtained as User", "e.g., NT AUTHORITY\\SYSTEM", "Command(s) Used",
        "Commands or steps used to locate/read the flag.", "Additional Notes",
        "Edit Machine", "New Machine", "Initialize Workspace", "Update Machine",
        "Edit Evidence", "Add Evidence", "Edit Evidence Block", "Record New Evidence",
        "Edit Vulnerability", "Add Vulnerability", "Register Vulnerability",
        "Edit Exploit", "Add Exploit", "Register Exploit",
        "Edit Flag", "Capture Flag",
        "Edit Screenshot", "Add Screenshot",
        "Vulnerability Title", "Attach Screenshots (Optional)", "You can paste images here directly using",
        "Type", "Severity", "CVE", "Affected Service / Component", "Affected Port / Protocol",
        "How was it identified?", "Evidence / Proof of Concept Snippet",
        "Technical Impact", "Remediation / Recommendation", "Sort Order",
        "Exploit Name / Title", "Objective", "URL / Reference", "Link to Identified Vulnerability",
        "Optional. Associates this exploit with a previously identified vulnerability.",
        "Local Path", "Target Service", "Target Port", "Command Executed", "Output",
        "Explanation", "Result / Outcome", "Timeline Order",
        "Platform", "Difficulty", "OS", "Status", "Report Language", "Report Type",
        "Client / Company Name", "Scope", "URLs, IP ranges, or domains included in this engagement.",
        "Author / Pentester", "Name to appear on the generated report cover.", "Executive Overview / Description",
        "No data recorded for this phase.", "Upload Screenshot"
    ]
    
    for s in common_strings:
        content = content.replace(f">{s}<", f">{{% trans \"{s}\" %}}<")
        content = content.replace(f"> {s} <", f"> {{% trans \"{s}\" }} <")
        content = content.replace(f">{s} ", f">{{% trans \"{s}\" }} ")
        content = content.replace(f" {s}<", f" {{% trans \"{s}\" }}<")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Done")
