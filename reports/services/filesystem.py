import os
import shutil
from pathlib import Path
from django.conf import settings
from slugify import slugify

def get_export_dir(machine):
    """
    Returns the absolute path to the export directory for a specific machine.
    Creates it if it doesn't exist.
    """
    machine_slug = slugify(machine.name)
    if not machine_slug:
        machine_slug = f"machine_{machine.pk}"
        
    export_path = os.path.join(settings.EXPORTS_ROOT, machine_slug)
    
    # Create main directory
    os.makedirs(export_path, exist_ok=True)
    
    # Create assets directory structure
    assets_dir = os.path.join(export_path, 'assets')
    screenshots_dir = os.path.join(assets_dir, 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)
    
    return export_path

def copy_screenshots_to_export(machine, export_dir):
    """
    Copies all screenshots associated with a machine to its export directory.
    Returns a mapping of original relative URLs to the new relative paths in the export directory.
    """
    screenshots_dir = os.path.join(export_dir, 'assets', 'screenshots')
    path_mapping = {}
    
    for screenshot in machine.screenshots.all():
        if screenshot.image and hasattr(screenshot.image, 'path'):
            source_path = screenshot.image.path
            if os.path.exists(source_path):
                filename = os.path.basename(source_path)
                # Sanitize filename to avoid LaTeX issues (remove spaces, special chars)
                safe_filename = slugify(os.path.splitext(filename)[0]) + os.path.splitext(filename)[1]
                
                dest_path = os.path.join(screenshots_dir, safe_filename)
                
                # Copy file
                shutil.copy2(source_path, dest_path)
                
                # Store the relative path as LaTeX will see it from main.tex
                path_mapping[screenshot.id] = f"assets/screenshots/{safe_filename}"
                
    return path_mapping
