TRANSLATIONS = {
    'en': {
        # main.tex.j2
        'ctf_writeup': 'CTF Writeup',
        'writeup_title_prefix': 'Writeup',
        'executive_summary': 'Executive Summary',
        'document_contains': 'This document contains the detailed exploitation report for',
        'table_of_contents': r'\tableofcontents',
        
        # General & Common
        'name': 'Name',
        'platform': 'Platform',
        'difficulty': 'Difficulty',
        'operating_system': 'Operating System',
        'target_ip': 'Target IP',
        'description': 'Description',
        'command': 'Command',
        'output': 'Output',
        'type': 'Type',
        'severity': 'Severity',
        'affected_service': 'Affected Service',
        'port': 'Port',
        'cve': 'CVE',
        'explanation': 'Explanation',
        'result': 'Result',
        'notes': 'Notes',
        'censored': '[CENSORED]',
        
        # overview.tex.j2
        'general_information': 'General Information',
        
        # reconnaissance.tex.j2
        'reconnaissance': 'Reconnaissance',
        'recon_desc': 'This phase involves active and passive information gathering.',
        'no_recon_evidence': 'No reconnaissance evidence gathered yet.',
        
        # vulnerabilities.tex.j2
        'vulnerabilities_identification': 'Vulnerability Identification',
        'vuln_desc': 'This section details the vulnerabilities identified.',
        'how_identified': 'How Identified',
        'impact': 'Impact',
        'recommendation': 'Recommendation',
        'no_vuln': 'No vulnerabilities identified yet.',
        
        # exploitation.tex.j2
        'exploitation': 'Exploitation',
        'exploit_desc': 'This phase details the exploitation process.',
        'objective': 'Objective',
        'exploit_type': 'Exploit Type',
        'local_path': 'Local Path',
        'command_used': 'Command Used',
        'no_exploit': 'No exploits documented yet.',
        
        # internal_recon.tex.j2
        'internal_recon': 'Internal Reconnaissance',
        'internal_recon_desc': 'Post-exploitation enumeration and internal discovery.',
        'no_internal_recon': 'No internal reconnaissance documented yet.',
        
        # user_movement.tex.j2
        'user_movement': 'User Movement',
        'user_movement_desc': 'Lateral movement and user pivoting activities.',
        'no_user_movement': 'No user movement documented yet.',
        
        # privilege_escalation.tex.j2
        'privilege_escalation': 'Privilege Escalation',
        'privilege_escalation_desc': 'Methods and actions taken to escalate privileges to root/SYSTEM.',
        'no_privilege_escalation': 'No privilege escalation actions documented yet.',
        
        # flags.tex.j2
        'flags': 'Flags',
        'value': 'Value',
        'location': 'Location',
        'user': 'User',
        'no_flags': 'No flags documented yet.',
        
        # conclusions.tex.j2
        'conclusions': 'Conclusions and Recommendations',
        'was_successfully_compromised': 'was successfully compromised.',
        'summary_of_vulnerabilities': 'Summary of Vulnerabilities',
        'no_specific_vulnerabilities': 'No specific vulnerabilities listed.',
        'general_recommendations': 'General Recommendations',
        'fix': 'Fix',
        'regularly_update': 'Regularly update systems and follow the principle of least privilege.',

        # Bug Bounty sections
        'client': 'Client',
        'author_label': 'Author',
        'no_description': 'No description provided.',
        'bb_summary': 'Executive Summary',
        'bb_finding': 'Vulnerability Finding',
        'bb_reproduction': 'Steps to Reproduce',
        'bb_impact': 'Impact',
        'bb_mitigation': 'Mitigation',
        'bb_proof': 'Proof of Concept',

        # Pentest sections
        'pt_executive': 'Executive Summary',
        'pt_scope': 'Scope of Work',
        'pt_findings': 'Findings Summary',
        'pt_no_scope': 'No scope defined.',

        # Markdown and LaTeX exports
        'overview': 'Overview',
        'vulnerability': 'Vulnerability',
        'affected': 'Affected',
        'exploit': 'Exploit',
        'outcome': 'Outcome',
        'phase': 'Phase',
        'evidence': 'Evidence',
        'additional_evidence': 'Additional Evidence',
        'additional_exploitation_evidence': 'Additional Exploitation Evidence',
        'target_vulnerability': 'Target Vulnerability',
        'commands': 'Command(s)',
        'the_machine': 'The machine',
        'reconnaissance_phase': 'Reconnaissance',
        'vulnerability_identification_phase': 'Vulnerability Identification',
        'exploitation_phase': 'Exploitation',
        'internal_reconnaissance_phase': 'Internal Reconnaissance',
        'user_movement_phase': 'User Movement',
        'privilege_escalation_phase': 'Privilege Escalation',
        'notes_phase': 'Notes'
    },
    'es': {
        # main.tex.j2
        'ctf_writeup': 'Reporte CTF',
        'writeup_title_prefix': 'Reporte',
        'executive_summary': 'Resumen Ejecutivo',
        'document_contains': 'Este documento contiene el reporte detallado de auditoría y explotación para',
        'table_of_contents': r'\renewcommand{\contentsname}{Índice}' + '\n' + r'\tableofcontents',
        
        # General & Common
        'name': 'Nombre',
        'platform': 'Plataforma',
        'difficulty': 'Dificultad',
        'operating_system': 'Sistema Operativo',
        'target_ip': 'IP Objetivo',
        'description': 'Descripción',
        'command': 'Comando',
        'output': 'Salida',
        'type': 'Tipo',
        'severity': 'Severidad',
        'affected_service': 'Servicio Afectado',
        'port': 'Puerto',
        'cve': 'CVE',
        'explanation': 'Explicación',
        'result': 'Resultado / Impacto',
        'notes': 'Notas',
        'censored': '[CENSURADO]',
        
        # overview.tex.j2
        'general_information': 'Información General',
        
        # reconnaissance.tex.j2
        'reconnaissance': 'Reconocimiento',
        'recon_desc': 'Esta fase involucra la recolección activa y pasiva de información.',
        'no_recon_evidence': 'Aún no se ha documentado evidencia de reconocimiento.',
        
        # vulnerabilities.tex.j2
        'vulnerabilities_identification': 'Identificación de Vulnerabilidades',
        'vuln_desc': 'Esta sección detalla las vulnerabilidades identificadas en el sistema.',
        'how_identified': 'Cómo fue identificada',
        'impact': 'Impacto',
        'recommendation': 'Recomendación',
        'no_vuln': 'Aún no se han identificado vulnerabilidades.',
        
        # exploitation.tex.j2
        'exploitation': 'Explotación',
        'exploit_desc': 'Esta fase detalla el proceso de explotación de las vulnerabilidades encontradas.',
        'objective': 'Objetivo',
        'exploit_type': 'Tipo de Exploit',
        'local_path': 'Ruta Local',
        'command_used': 'Comando Utilizado',
        'no_exploit': 'Aún no se han documentado exploits.',
        
        # internal_recon.tex.j2
        'internal_recon': 'Reconocimiento Interno',
        'internal_recon_desc': 'Enumeración y descubrimiento interno tras la explotación inicial.',
        'no_internal_recon': 'Aún no se ha documentado reconocimiento interno.',
        
        # user_movement.tex.j2
        'user_movement': 'Movimiento Lateral / Salto de Usuario',
        'user_movement_desc': 'Actividades de movimiento lateral y acceso a otros usuarios en el sistema.',
        'no_user_movement': 'Aún no se ha documentado movimiento lateral.',
        
        # privilege_escalation.tex.j2
        'privilege_escalation': 'Escalada de Privilegios',
        'privilege_escalation_desc': 'Métodos y acciones realizadas para escalar privilegios a root/SYSTEM.',
        'no_privilege_escalation': 'Aún no se han documentado acciones de escalada de privilegios.',
        
        # flags.tex.j2
        'flags': 'Banderas (Flags)',
        'value': 'Valor',
        'location': 'Ubicación',
        'user': 'Usuario',
        'no_flags': 'Aún no se han documentado banderas.',
        
        # conclusions.tex.j2
        'conclusions': 'Conclusiones y Recomendaciones',
        'was_successfully_compromised': 'fue comprometida exitosamente.',
        'summary_of_vulnerabilities': 'Resumen de Vulnerabilidades',
        'no_specific_vulnerabilities': 'No se listaron vulnerabilidades específicas.',
        'general_recommendations': 'Recomendaciones Generales',
        'fix': 'Solucionar',
        'regularly_update': 'Mantenga los sistemas actualizados regularmente y aplique el principio de mínimo privilegio.',

        # Bug Bounty sections
        'client': 'Cliente',
        'author_label': 'Autor',
        'no_description': 'Sin descripción proporcionada.',
        'bb_summary': 'Resumen Ejecutivo',
        'bb_finding': 'Hallazgo de Vulnerabilidad',
        'bb_reproduction': 'Pasos para Reproducir',
        'bb_impact': 'Impacto',
        'bb_mitigation': 'Mitigación',
        'bb_proof': 'Prueba de Concepto',

        # Pentest sections
        'pt_executive': 'Resumen Ejecutivo',
        'pt_scope': 'Alcance del Trabajo',
        'pt_findings': 'Resumen de Hallazgos',
        'pt_no_scope': 'No se definió un alcance.',

        # Markdown and LaTeX exports
        'overview': 'Resumen',
        'vulnerability': 'Vulnerabilidad',
        'affected': 'Afectado',
        'exploit': 'Exploit',
        'outcome': 'Resultado',
        'phase': 'Fase',
        'evidence': 'Evidencia',
        'additional_evidence': 'Evidencia adicional',
        'additional_exploitation_evidence': 'Evidencia adicional de explotación',
        'target_vulnerability': 'Vulnerabilidad objetivo',
        'commands': 'Comando(s)',
        'the_machine': 'La máquina',
        'reconnaissance_phase': 'Reconocimiento',
        'vulnerability_identification_phase': 'Identificación de Vulnerabilidades',
        'exploitation_phase': 'Explotación',
        'internal_reconnaissance_phase': 'Reconocimiento Interno',
        'user_movement_phase': 'Movimiento Lateral / Salto de Usuario',
        'privilege_escalation_phase': 'Escalada de Privilegios',
        'notes_phase': 'Notas'
    }
}

def get_i18n(lang_code):
    return TRANSLATIONS.get(lang_code, TRANSLATIONS['en'])
