from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import json
import os

from django.db import transaction
from django.http import FileResponse, HttpResponse, Http404, HttpResponseBadRequest, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from .models import Machine, Evidence, Vulnerability, Exploit, Screenshot, Flag
from .forms import MachineForm, EvidenceForm, VulnerabilityForm, ExploitForm, ScreenshotForm, FlagForm

# --- Machine Views ---

def machine_list(request):
    machines = Machine.objects.all().order_by('-updated_at')
    return render(request, 'reports/machine_list.html', {'machines': machines})

@ensure_csrf_cookie
def machine_detail(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    
    # Group evidences by phase
    evidences_by_phase = {}
    timeline_phases = {}
    for choice in Evidence.Phase.choices:
        phase_id = choice[0]
        phase_data = {
            'name': choice[1],
            'evidences': machine.evidences.filter(phase=phase_id)
        }
        evidences_by_phase[phase_id] = phase_data
        if phase_id != Evidence.Phase.NOTES:
            timeline_phases[phase_id] = phase_data
        
    context = {
        'machine': machine,
        'evidences_by_phase': evidences_by_phase,
        'timeline_phases': timeline_phases,
        'notes_phase': evidences_by_phase[Evidence.Phase.NOTES],
        'vulnerabilities': machine.vulnerabilities.all(),
        'exploits': machine.exploits.all(),
        'screenshots': machine.screenshots.all(),
        'flags': machine.flags.all(),
    }
    return render(request, 'reports/machine_detail.html', context)

def machine_create(request):
    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            machine = form.save()
            messages.success(request, 'Machine created successfully.')
            return redirect('reports:machine_detail', pk=machine.pk)
    else:
        form = MachineForm()
    return render(request, 'reports/machine_form.html', {'form': form})

def machine_edit(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    if request.method == 'POST':
        form = MachineForm(request.POST, instance=machine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Machine updated successfully.')
            return redirect('reports:machine_detail', pk=machine.pk)
    else:
        form = MachineForm(instance=machine)
    return render(request, 'reports/machine_form.html', {'form': form, 'machine': machine})

def machine_delete(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    if request.method == 'POST':
        machine.delete()
        messages.success(request, 'Machine deleted successfully.')
        return redirect('reports:machine_list')
    return render(request, 'reports/confirm_delete.html', {'object': machine, 'cancel_url': reverse('reports:machine_detail', args=[machine.pk])})

# --- Evidence Views ---

def evidence_create(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES)
        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.machine = machine
            evidence.save()
            for f in request.FILES.getlist('screenshots'):
                Screenshot.objects.create(
                    machine=machine,
                    evidence=evidence,
                    phase=evidence.phase,
                    image=f,
                    caption=f"{evidence.title} - Attachment"
                )
            messages.success(request, 'Evidence added.')
            if request.htmx:
                return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
            return redirect('reports:machine_detail', pk=machine.pk)
    else:
        initial = {'phase': request.GET.get('phase', Evidence.Phase.RECON)}
        form = EvidenceForm(initial=initial)
    template_name = 'reports/evidence_form.html'
    return render(request, template_name, {'form': form, 'machine': machine})

def evidence_edit(request, machine_id, pk):
    machine = get_object_or_404(Machine, pk=machine_id)
    evidence = get_object_or_404(Evidence, pk=pk, machine=machine)
    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES, instance=evidence)
        if form.is_valid():
            form.save()
            for f in request.FILES.getlist('screenshots'):
                Screenshot.objects.create(
                    machine=machine,
                    evidence=evidence,
                    phase=evidence.phase,
                    image=f,
                    caption=f"{evidence.title} - Attachment"
                )
            messages.success(request, 'Evidence updated.')
            if request.htmx:
                return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
            return redirect('reports:machine_detail', pk=machine.pk)
    else:
        form = EvidenceForm(instance=evidence)
    return render(request, 'reports/evidence_form.html', {'form': form, 'machine': machine, 'evidence': evidence})

def evidence_delete(request, machine_id, pk):
    evidence = get_object_or_404(Evidence, pk=pk, machine_id=machine_id)
    if request.method == 'POST':
        evidence.delete()
        messages.success(request, 'Evidence deleted.')
        if request.htmx:
            return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
        return redirect('reports:machine_detail', pk=machine_id)
    return render(request, 'reports/confirm_delete.html', {'object': evidence, 'cancel_url': reverse('reports:machine_detail', args=[machine_id])})

# --- Vulnerability Views ---

def vulnerability_create(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    if request.method == 'POST':
        form = VulnerabilityForm(request.POST, request.FILES)
        if form.is_valid():
            vuln = form.save(commit=False)
            vuln.machine = machine
            vuln.save()
            for f in request.FILES.getlist('screenshots'):
                Screenshot.objects.create(
                    machine=machine,
                    vulnerability=vuln,
                    phase=Evidence.Phase.VULN_ID,
                    image=f,
                    caption=f"{vuln.title} - Attachment"
                )
            messages.success(request, 'Vulnerability added.')
            if request.htmx:
                return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
            return redirect('reports:machine_detail', pk=machine.pk)
    else:
        form = VulnerabilityForm()
    return render(request, 'reports/vulnerability_form.html', {'form': form, 'machine': machine})

def vulnerability_edit(request, machine_id, pk):
    machine = get_object_or_404(Machine, pk=machine_id)
    vuln = get_object_or_404(Vulnerability, pk=pk, machine=machine)
    if request.method == 'POST':
        form = VulnerabilityForm(request.POST, request.FILES, instance=vuln)
        if form.is_valid():
            form.save()
            for f in request.FILES.getlist('screenshots'):
                Screenshot.objects.create(
                    machine=machine,
                    vulnerability=vuln,
                    phase=Evidence.Phase.VULN_ID,
                    image=f,
                    caption=f"{vuln.title} - Attachment"
                )
            messages.success(request, 'Vulnerability updated.')
            if request.htmx:
                return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
            return redirect('reports:machine_detail', pk=machine.pk)
    else:
        form = VulnerabilityForm(instance=vuln)
    return render(request, 'reports/vulnerability_form.html', {'form': form, 'machine': machine, 'vulnerability': vuln})

def vulnerability_delete(request, machine_id, pk):
    vuln = get_object_or_404(Vulnerability, pk=pk, machine_id=machine_id)
    if request.method == 'POST':
        vuln.delete()
        messages.success(request, 'Vulnerability deleted.')
        if request.htmx:
            return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
        return redirect('reports:machine_detail', pk=machine_id)
    return render(request, 'reports/confirm_delete.html', {'object': vuln, 'cancel_url': reverse('reports:machine_detail', args=[machine_id])})

# --- Exploit Views ---

def exploit_create(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    if request.method == 'POST':
        form = ExploitForm(request.POST, request.FILES, machine=machine)
        if form.is_valid():
            exploit = form.save(commit=False)
            exploit.machine = machine
            exploit.save()
            for f in request.FILES.getlist('screenshots'):
                Screenshot.objects.create(
                    machine=machine,
                    exploit=exploit,
                    phase=Evidence.Phase.EXPLOIT,
                    image=f,
                    caption=f"{exploit.name} - Attachment"
                )
            messages.success(request, 'Exploit added.')
            if request.htmx:
                return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
            return redirect('reports:machine_detail', pk=machine.pk)
    else:
        form = ExploitForm(machine=machine)
    return render(request, 'reports/exploit_form.html', {'form': form, 'machine': machine})

def exploit_edit(request, machine_id, pk):
    machine = get_object_or_404(Machine, pk=machine_id)
    exploit = get_object_or_404(Exploit, pk=pk, machine=machine)
    if request.method == 'POST':
        form = ExploitForm(request.POST, request.FILES, instance=exploit, machine=machine)
        if form.is_valid():
            form.save()
            for f in request.FILES.getlist('screenshots'):
                Screenshot.objects.create(
                    machine=machine,
                    exploit=exploit,
                    phase=Evidence.Phase.EXPLOIT,
                    image=f,
                    caption=f"{exploit.name} - Attachment"
                )
            messages.success(request, 'Exploit updated.')
            if request.htmx:
                return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
            return redirect('reports:machine_detail', pk=machine.pk)
    else:
        form = ExploitForm(instance=exploit, machine=machine)
    return render(request, 'reports/exploit_form.html', {'form': form, 'machine': machine, 'exploit': exploit})

def exploit_delete(request, machine_id, pk):
    exploit = get_object_or_404(Exploit, pk=pk, machine_id=machine_id)
    if request.method == 'POST':
        exploit.delete()
        messages.success(request, 'Exploit deleted.')
        if request.htmx:
            return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
        return redirect('reports:machine_detail', pk=machine_id)
    return render(request, 'reports/confirm_delete.html', {'object': exploit, 'cancel_url': reverse('reports:machine_detail', args=[machine_id])})

# --- Screenshot Views ---

def screenshot_create(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    if request.method == 'POST':
        form = ScreenshotForm(request.POST, request.FILES, machine=machine)
        if form.is_valid():
            screenshot = form.save(commit=False)
            screenshot.machine = machine
            screenshot.save()
            messages.success(request, 'Screenshot uploaded.')
            if request.htmx:
                return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
            return redirect('reports:machine_detail', pk=machine.pk)
    else:
        form = ScreenshotForm(machine=machine)
    return render(request, 'reports/screenshot_form.html', {'form': form, 'machine': machine})

def screenshot_delete(request, machine_id, pk):
    screenshot = get_object_or_404(Screenshot, pk=pk, machine_id=machine_id)
    if request.method == 'POST':
        screenshot.delete()
        messages.success(request, 'Screenshot deleted.')
        if request.htmx:
            return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
        return redirect('reports:machine_detail', pk=machine_id)
    return render(request, 'reports/confirm_delete.html', {'object': screenshot, 'cancel_url': reverse('reports:machine_detail', args=[machine_id])})

# --- Flag Views ---

def flag_create(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    if request.method == 'POST':
        form = FlagForm(request.POST)
        if form.is_valid():
            flag = form.save(commit=False)
            flag.machine = machine
            flag.save()
            messages.success(request, 'Flag added.')
            if request.htmx:
                return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
            return redirect('reports:machine_detail', pk=machine.pk)
    else:
        form = FlagForm()
    return render(request, 'reports/flag_form.html', {'form': form, 'machine': machine})

def flag_edit(request, machine_id, pk):
    machine = get_object_or_404(Machine, pk=machine_id)
    flag = get_object_or_404(Flag, pk=pk, machine=machine)
    if request.method == 'POST':
        form = FlagForm(request.POST, instance=flag)
        if form.is_valid():
            form.save()
            messages.success(request, 'Flag updated.')
            if request.htmx:
                return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
            return redirect('reports:machine_detail', pk=machine.pk)
    else:
        form = FlagForm(instance=flag)
    return render(request, 'reports/flag_form.html', {'form': form, 'machine': machine, 'flag': flag})

def flag_delete(request, machine_id, pk):
    flag = get_object_or_404(Flag, pk=pk, machine_id=machine_id)
    if request.method == 'POST':
        flag.delete()
        messages.success(request, 'Flag deleted.')
        if request.htmx:
            return HttpResponse(status=204, headers={'HX-Refresh': 'true'})
        return redirect('reports:machine_detail', pk=machine_id)
    return render(request, 'reports/confirm_delete.html', {'object': flag, 'cancel_url': reverse('reports:machine_detail', args=[machine_id])})

# --- Export Views ---

def export_view(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    return render(request, 'reports/export.html', {'machine': machine})

def export_latex(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    try:
        from .services.latex_renderer import render_machine_to_latex
        export_dir, main_tex_path = render_machine_to_latex(machine)
        messages.success(request, f'LaTeX exported successfully to {main_tex_path}')
    except Exception as e:
        messages.error(request, f'Error generating LaTeX: {str(e)}')
    return redirect('reports:export_view', machine_id=machine_id)

def export_pdf(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    try:
        from .services.latex_renderer import render_machine_to_latex
        from .services.pdf_builder import build_pdf
        from slugify import slugify
        
        machine_slug = slugify(machine.name) or f"machine_{machine.pk}"
        export_dir, _ = render_machine_to_latex(machine)
        
        success, output = build_pdf(export_dir)
        if success:
            pdf_path = os.path.join(export_dir, 'main.pdf')
            return FileResponse(
                open(pdf_path, 'rb'),
                as_attachment=True,
                filename=f'{machine_slug}.pdf',
                content_type='application/pdf',
            )
        messages.error(request, f'PDF generation failed. Log: {output[:500]}...')
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        
    return redirect('reports:export_view', machine_id=machine_id)

def export_markdown(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    try:
        from .services.markdown_exporter import build_markdown_zip

        archive_bytes, filename = build_markdown_zip(machine)
        response = HttpResponse(archive_bytes, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        messages.error(request, f'Error generating Markdown export: {str(e)}')
        return redirect('reports:export_view', machine_id=machine_id)

@require_POST
def reorder_items(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON payload.')

    item_type = payload.get('type')
    ids = payload.get('ids')
    if item_type not in {'evidence', 'vulnerability', 'exploit'} or not isinstance(ids, list):
        return HttpResponseBadRequest('Invalid reorder payload.')

    model_map = {
        'evidence': Evidence,
        'vulnerability': Vulnerability,
        'exploit': Exploit,
    }
    model = model_map[item_type]

    try:
        ordered_ids = [int(item_id) for item_id in ids]
    except (TypeError, ValueError):
        return HttpResponseBadRequest('Invalid item IDs.')

    owned_count = model.objects.filter(machine=machine, pk__in=ordered_ids).count()
    if owned_count != len(set(ordered_ids)):
        return HttpResponseBadRequest('One or more items do not belong to this machine.')

    with transaction.atomic():
        for index, item_id in enumerate(ordered_ids, start=1):
            model.objects.filter(machine=machine, pk=item_id).update(order=index)

    return JsonResponse({'status': 'ok'})
