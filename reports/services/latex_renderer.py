import os
import jinja2
from django.conf import settings
from django.utils import translation
from .filesystem import get_export_dir, copy_screenshots_to_export
from .latex_escape import escape_latex
from .i18n import get_i18n
from reports.models import Evidence

def setup_jinja_env():
    """
    Sets up a Jinja2 environment configured for LaTeX templates.
    Uses custom delimiters to avoid conflict with standard LaTeX syntax.
    """
    template_dir = os.path.join(settings.BASE_DIR, 'reports', 'latex_templates')
    
    # If the templates directory doesn't exist, we'll get an error, but it should be created by the setup process
    os.makedirs(os.path.join(template_dir, 'sections'), exist_ok=True)
    
    env = jinja2.Environment(
        block_start_string=r'\BLOCK{',
        block_end_string='}',
        variable_start_string=r'\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(template_dir)
    )
    
    # Add custom filters
    env.filters['escape_tex'] = escape_latex
    
    return env

def render_machine_to_latex(machine):
    """
    Gathers all data for a machine, prepares the export directory,
    copies assets, and renders the Jinja2 templates into a main.tex file.
    """
    export_dir = get_export_dir(machine)
    screenshot_paths = copy_screenshots_to_export(machine, export_dir)
    
    # Group evidences by phase
    evidences_by_phase = {}
    for choice in Evidence.Phase.choices:
        phase_id = choice[0]
        evidences_by_phase[phase_id] = list(machine.evidences.filter(phase=phase_id))

    has_phase_content = {
        phase_id: bool(evidences)
        for phase_id, evidences in evidences_by_phase.items()
    }
    has_vulnerability_section = bool(machine.vulnerabilities.exists() or has_phase_content.get(Evidence.Phase.VULN_ID))
    has_exploitation_section = bool(machine.exploits.exists() or has_phase_content.get(Evidence.Phase.EXPLOIT))
    has_bug_bounty_reproduction = any(
        has_phase_content.get(phase_id)
        for phase_id in [Evidence.Phase.RECON, Evidence.Phase.VULN_ID, Evidence.Phase.EXPLOIT]
    )
    has_vulnerability_impact = any(bool(vuln.impact) for vuln in machine.vulnerabilities.all())
    has_vulnerability_recommendations = any(bool(vuln.recommendation) for vuln in machine.vulnerabilities.all())
    
    # Prepare context
    i18n_strings = get_i18n(machine.report_language)
    phase_labels = {
        phase_id: i18n_strings.get(f"{phase_id}_phase", phase_name)
        for phase_id, phase_name in Evidence.Phase.choices
    }
    context = {
        'machine': machine,
        'evidences_by_phase': evidences_by_phase,
        'vulnerabilities': list(machine.vulnerabilities.all()),
        'exploits': list(machine.exploits.all()),
        'flags': list(machine.flags.all()),
        'screenshot_paths': screenshot_paths,  # map screenshot ID -> relative path
        'i18n': i18n_strings,
        'phase_labels': phase_labels,
        'has_phase_content': has_phase_content,
        'has_vulnerability_section': has_vulnerability_section,
        'has_exploitation_section': has_exploitation_section,
        'has_bug_bounty_reproduction': has_bug_bounty_reproduction,
        'has_vulnerability_impact': has_vulnerability_impact,
        'has_vulnerability_recommendations': has_vulnerability_recommendations,
        'has_flags': machine.flags.exists(),
        'has_pt_scope': bool(machine.scope or machine.target_ip),
        'has_machine_description': bool(machine.description),
    }
    
    env = setup_jinja_env()
    
    TEMPLATE_MAP = {
        'ctf': 'main.tex.j2',
        'bug_bounty': 'main_bug_bounty.tex.j2',
        'pentest': 'main_pentest.tex.j2',
    }
    template_name = TEMPLATE_MAP.get(getattr(machine, 'report_type', 'ctf'), 'main.tex.j2')
    
    try:
        template = env.get_template(template_name)
        with translation.override(machine.report_language):
            rendered_latex = template.render(**context)
    except jinja2.exceptions.TemplateNotFound as e:
        raise Exception(f"LaTeX template not found: {e}. Please ensure the latex_templates directory is properly populated.")
    
    # Write the output
    main_tex_path = os.path.join(export_dir, 'main.tex')
    with open(main_tex_path, 'w', encoding='utf-8') as f:
        f.write(rendered_latex)
        
    return export_dir, main_tex_path
