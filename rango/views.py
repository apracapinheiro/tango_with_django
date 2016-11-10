# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render
from .models import Page, Category


# Create your views here.


def index(request):
    """Constroi um dicionario para passar para o template o contexto"""
    # A query retorna a lista de categorias ordenada pela qtde de likes em ordem descendente, retorna
    # somente as 5 primeiras categorias
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    return HttpResponse("Rango about <br> <a href='/rango/'>Index</a>")


def show_category(request, category_name_slug):
    """Cria um dicionario de contexto que será passado para o template"""
    context_dict = {}

    try:
        # Se o nome slug de uma categoria não for encontrada o método .get() devolve uma exceção DoesNotExist
        # Se o nome slug for encontrado o método .get() retorna a instância de um model ou a exceção
        category = Category.objects.get(slug=category_name_slug)

        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        # Se nenhuma categoria for encontrada o template irá mostrar uma mensagem 'no category'
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context_dict)