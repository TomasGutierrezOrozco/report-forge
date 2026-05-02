import os
import shutil

from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from slugify import slugify

from reports.models import Machine, Screenshot


@receiver(post_delete, sender=Screenshot)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem when corresponding `Screenshot` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(post_delete, sender=Machine)
def auto_delete_directories_on_delete(sender, instance, **kwargs):
    """
    Deletes the export and media directories associated with a machine when it is deleted.
    """
    machine_slug = slugify(instance.name)
    if not machine_slug:
        machine_slug = f"machine_{instance.pk}"

    # Delete the exports directory
    export_dir = os.path.join(settings.EXPORTS_ROOT, machine_slug)
    if os.path.isdir(export_dir):
        shutil.rmtree(export_dir)

    # Delete the machine's media directory
    media_dir = os.path.join(settings.MEDIA_ROOT, 'screenshots', machine_slug)
    if os.path.isdir(media_dir):
        shutil.rmtree(media_dir)
