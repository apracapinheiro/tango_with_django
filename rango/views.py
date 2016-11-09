# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def index(request):
    """Constroi um dicionario para passar para o template o contexto"""
    context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    return HttpResponse("Rango about <br> <a href='/rango/'>Index</a>")