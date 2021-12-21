from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
import markdown2
from . import util
from django import forms
import random

class SearchForm(forms.Form) :
    q = forms.CharField()

class NewEntryForm(forms.Form) :
    title = forms.CharField()
    markdown  = forms.CharField()

class EditEntryForm(NewEntryForm) :
    pass


def index(request):
    return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(),
            "form" : SearchForm(),
            })


def show_entry(request, entry):
    message = None
    markdown = util.get_entry(entry)
    if not markdown :
        message = {'text': 'Page "'+entry+'" not found', 'color': 'warning'}
        return render(request, "encyclopedia/error.html", {
            "message": message,
            })
    html = markdown2.markdown(markdown)
    return render(request, "encyclopedia/show_entry.html", {
            "entry": entry,
            "markdown": markdown,
            "html": html,
            })


def search(request):
    entries = []
    message = None

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search_string = form.cleaned_data["q"]
            all_entries = util.list_entries()
            for entry in all_entries :
                if search_string.lower()==entry.lower() :
                    return show_entry(request, entry)
                if search_string.lower() in entry.lower() :
                    entries.append(entry)
    if len(entries)==0 :
        message = {'text': 'No page with "'+search_string+'" in title found', 'color': 'warning'}

    return render(request, "encyclopedia/index.html", {
            "entries": entries,
            "form": SearchForm(),
            "search_string": search_string,
            "message": message,
            })


def new_entry(request):

    title = ''
    markdown = ''
    message = None

    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            markdown = form.cleaned_data["markdown"]
            if title=='' :
                message = {'text': 'No title', 'color': 'danger'}
            else :
                all_entries = util.list_entries()
                for entry in all_entries :
                    if title.lower()==entry.lower() :
                        message = {'text': 'This page already exsists', 'color': 'warning'}
                        return render(request, "encyclopedia/new_entry.html", {
                                "title": title,
                                "markdown": markdown,
                                "message": message,
                                })

                if markdown=='' :
                    message = {'text': 'No markdown', 'color': 'danger'}
                else :
                    util.save_entry(title, markdown)
                    message = {'text': 'New entry successfully created', 'color': 'success'}
                    return show_entry(request, title)
        else :
            message = {'text': form.errors, 'color': 'danger'}

    return render(request, "encyclopedia/new_entry.html", {
            "title": title,
            "markdown": markdown,
            "message": message,
            })


def edit_entry(request):

    title = ''
    markdown = ''
    message = {'text': 'Page '+title+' is ready to be edited', 'color': 'info'}

    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            markdown = form.cleaned_data["markdown"]
            if title=='' :
                message = {'text': 'No title', 'color': 'danger'}
            else :
                if markdown=='' :
                    message = {'text': 'No markdown', 'color': 'danger'}
                else :
                    util.save_entry(title, markdown)
                    message = {'text': 'New entry successfully created', 'color': 'success'}
                    return show_entry(request, title)
        else :
            message = {'text': form.errors, 'color': 'danger'}
    else :
        form = EditEntryForm(request.GET)
        if form.is_valid():
            title = form.cleaned_data["title"]
            markdown = form.cleaned_data["markdown"]
            if title=='' :
                message = {'text': 'No title', 'color': 'danger'}
            else :
                if markdown=='' :
                    message = {'text': 'No markdown', 'color': 'danger'}
        else :
            message = {'text': form.errors, 'color': 'danger'}

    return render(request, "encyclopedia/edit_entry.html", {
            "title": title,
            "markdown": markdown,
            "message": message,
            })

def random_entry(request):

    all_entries = util.list_entries()
    number_of_entries = len(all_entries)
    random_entry = all_entries[random.randint(0, number_of_entries-1)]
    return show_entry(request, random_entry)



