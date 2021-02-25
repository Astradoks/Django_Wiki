from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
from random import randint
import markdown2
from . import util

class SearchForm(forms.Form):
    q = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia', 'class': 'search'}))

class CreateForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': 'form-control container'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control container'}))

class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control container'}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def entry(request, title):
    if util.get_entry(title):
        entry_body = markdown2.markdown(util.get_entry(title))
    else:
        entry_body = util.get_entry(title)
    return render(request, "encyclopedia/entry.html", {
        "entry_title": title,
        "entry_body": entry_body,
        "form": SearchForm()
    })

def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            q = form.cleaned_data["q"]
            if util.get_entry(q) == None:
                all_entries = util.list_entries()
                entries = []
                for entry in all_entries:
                    if q.lower() in entry.lower():
                        entries.append(entry)
                return render(request, "encyclopedia/search.html", {
                    "form": form,
                    "entries" : entries
                })
            else:
                return HttpResponseRedirect(reverse("wiki:entry", args=[q]))
        else:
            return render(request, "encyclopedia/search.html", {
                "form": form
            })
    return render(request, "encyclopedia/search.html", {
        "form": SearchForm()
    })

def create(request):
    all_entries = util.list_entries()
    title = ''
    if request.method == "POST":
        create_form = CreateForm(request.POST)
        if create_form.is_valid():
            title = create_form.cleaned_data["title"]
            content = create_form.cleaned_data["content"]
            if title not in all_entries:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("wiki:entry", args=[title]))
            else:
                return render(request, "encyclopedia/create.html", {
                    "form": SearchForm(), 
                    "create_form": create_form,
                    "all_entries": all_entries,
                    "title": title
                })
        else:
            return render(request, "encyclopedia/create.html", {
                "form": SearchForm(), 
                "create_form": create_form,
                "all_entries": all_entries,
                "title": title
            })
    return render(request, "encyclopedia/create.html", {
        "form": SearchForm(),
        "create_form": CreateForm(),
        "all_entries": all_entries,
        "title": title
    })

def edit(request, title):
    entry = util.get_entry(title)
    if request.method == "POST":
        edit_form = EditForm(request.POST)
        if edit_form.is_valid():
            content = edit_form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("wiki:entry", args=[title]))
        else:
            return render(request, "encyclopedia/edit.html", {
                "form": SearchForm(),
                "edit_form": EditForm({'content': entry}),
                "entry_title": title
            })
    return render(request, "encyclopedia/edit.html", {
        "form": SearchForm(),
        "edit_form": EditForm({'content': entry}),
        "entry_title": title
    })

def random(request):
    all_entries = util.list_entries()
    value = randint(0, len(all_entries) - 1)
    return HttpResponseRedirect(reverse("wiki:entry", args=[all_entries[value]]))