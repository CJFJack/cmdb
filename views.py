from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.template.loader import get_template
import markdown

# Create your views here.


def index(request):
    """首页"""
    if request.method == "GET":
        head = {'username': request.user.username}
        if request.user.is_superuser:
            return HttpResponseRedirect('/dashboard/')
        else:
            return render(request, 'myindex.html', {'head': head})


def cmdb_release_notes(request):
    """cmdb更新日志"""
    if request.method == 'GET':
        if request.user.is_superuser:
            template = get_template('cmdb_release_notes.html')
            docfile = get_template('cmdb_release_notes.md')
            content = docfile.render()
            html = template.render({
                'request': request,
                'content':
                    markdown.markdown(content,
                                      extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          'markdown.extensions.toc',
                                      ])
            })
            return HttpResponse(html)
        else:
            return render(request, '403.html')

