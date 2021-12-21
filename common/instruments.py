import os

def empty_folder(folder) :                # -------------- EMPTY_FOLDER --------
    files = os.listdir(folder)
    for file in files :
        os.remove(folder + '/' + file)

def dir_size(folder):
    size = 0
    for root, dirs, files in os.walk(folder):
        for f in files:
            fp = os.path.join(root, f)
            size += os.path.getsize(fp)
    return size

# -------------- FILE_TREE -----------
def file_tree(startpath, n_levels=1, hide_folders=[]) :
    tree = []

    for root, dirs, files in os.walk(startpath):
        dir_item = {}

        level = root.replace(startpath, '').count(os.sep)
        if level > n_levels:
            continue

        dir_item['level'] = level
        dir_item['type'] = 'dir'
        dir_item['size'] = dir_size(root)
        dir_name = os.path.basename(root)

        if level == 0:
            parent_names = root.split('/')
            parents = []
            link = '?'
            for name in parent_names:
                if name != '':
                    link += name + '?'
                    item = {}
                    item['name'] = name
                    item['link'] = link[:-1] #.strip('?')
                    parents.append(item)
            dir_item['parents'] = parents

        if not dir_name in hide_folders :
            dir_item['name'] = dir_name
            dir_item['dir'] = root
            dir_item['link'] = root.replace('/', '?')
            file_list = []
            file_sizes = []
            dir_sizes = []
            if level < n_levels:
                for f in files:
                    ext = os.path.splitext(f)[1]
                    file_item ={}
                    file_item['level'] = level + 1
                    file_item['type'] = 'file'
                    file_item['name'] = f
                    file_item['dir'] = root # [len(settings.STATIC):]
                    if ext=='.py' :
                        file_item['type'] = 'module'

                    fp = os.path.join(root, f)
                    size = os.path.getsize(fp)
                    file_item['size'] = size
                    file_list.append(file_item)

                    file_sizes_item = {}
                    file_sizes_item['name'] = f
                    file_sizes_item['size'] = size
                    file_sizes.append(file_sizes_item)


                for dir in dirs:
                    file_sizes_item = {}
                    file_sizes_item['name'] = dir
                    file_sizes_item['size'] = dir_size(os.path.join(root, dir))
                    dir_sizes.append(file_sizes_item)


            dir_item['file_sizes'] = file_sizes
            dir_item['dir_sizes'] = dir_sizes

            tree.append(dir_item)
            tree += file_list
    return tree

#___________________________________________________________ MARKDOWN __________

from django.shortcuts import render
from django.core.files.storage import default_storage

import markdown

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

def show_md(request, entry_rus=None, entry_eng=None, entry=None, layout=None):
    '''
    Shows the .md entry
    '''
    context = {}
    if layout:
        context['layout'] = layout
    if entry:
        md = get_entry(entry)
        html = markdown.markdown(md)
        context['html'] = html
    if entry_rus:
        md_rus = get_entry(entry_rus)
        html_rus = markdown.markdown(md_rus)
        context['html_rus'] = html_rus
    if entry_eng:
        md_eng = get_entry(entry_eng)
        html_eng = markdown.markdown(md_eng)
        context['html_eng'] = html_eng
    return render(request, "common/show_md.html", context)

