# -*- coding: utf-8 -*-

from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Page, Category
from .forms import CategoryForm, PageForm, UserForm, UserProfileForm


# Create your views here.


def index(request):
    """Constroi um dicionario para passar para o template o contexto"""
    # A query retorna a lista de categorias ordenada pela qtde de likes em ordem descendente, retorna
    # somente as 5 primeiras categorias
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    print (request.method)
    print (request.user)
    return render(request, 'rango/about.html', {})


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


def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print (form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print (form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    # Um valor booleano para dizer ao template se o registro teve sucesso.
    # Definido como False inicialmente. O código altera o valor para True quando o registro for cadastrado.
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # agora será realizado o hash do password com o método set_password
            # após o hash, o objeto user é atualizado
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            # se o usuário forneceu uma imagem de profile, então é necessário pegar do input form e coloca-la
            # no model UserProfile
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            # atualiza a variavel registered para indicar que o template de registro teve sucesso.
            registered = True
        else:
            # imprimir possiveis erros no terminal
            print (user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', {'user_form': user_form,
                                                   'profile_form': profile_form,
                                                   'registered': registered})


def user_login(request):
    if request.method == 'POST':
        # É utilizado request.POST.get('variable') em vez de request.POST['variable']
        # porque request.POST.get('variable') retorna None se o valor não existir, enquanto request.POST['variable']
        # implicará em um erro de exceção KeyError
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your Rango account is disabled")
        else:
            print ("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied")

    else:
        return render(request, 'rango/login.html', {})