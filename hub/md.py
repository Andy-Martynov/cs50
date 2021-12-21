import re

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render

import markdown2

def list_entries():
    """
    Returns a list of all names of md entries.
    """
    _, filenames = default_storage.listdir("")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an md entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = title
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an md entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(title)
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None


def show_entry(request, entry):
    error = None
    markdown = get_entry(entry)
    if not markdown :
        error = f'entry {entry} not found'
        return JsonResponse({'status':'404', 'entry':entry, 'html':None, 'error':error})

    html = markdown2.markdown(markdown)
    return JsonResponse({'status':'200', 'entry':entry, 'html':html, 'error':None})















