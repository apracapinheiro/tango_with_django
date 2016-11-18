# -*- coding: utf-8 -*-

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from registration.backends.simple.views import RegistrationView
from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import datetime
from rango.bing_search import run_query

from .models import Page, Category, UserProfile
from .forms import CategoryForm, PageForm, UserForm, UserProfileForm


# Create your views here.


class MyRegistrationView(RegistrationView):
    def get_sucess_url(self, user):
        return reverse('register_profile')


def index(request):
    """Constroi um dicionario para passar para o template o contexto"""
    # A query retorna a lista de categorias ordenada pela qtde de likes em ordem descendente, retorna
    # somente as 5 primeiras categorias
    # request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    # visitor_cookie_handler(request)
    # context_dict['visits'] = request.session['visits']
    # print(request.session['visits'])

    response = render(request, 'rango/index.html', context=context_dict)

    return response


def about(request):
    # if request.session.test_cookie_worked():
    #     print("TEST COOKIE WORKED!")
    #     request.session.delete_test_cookie()
    # To complete the exercise in chapter 4, we need to remove the following line
    # return HttpResponse("Rango says here is the about page. <a href='/rango/'>View index page</a>")

    # and replace it with a pointer to ther about.html template using the render method
    return render(request, 'rango/about.html', {})


# def visitor_cookie_handler(request, response):
#     # Pega o numero de visitas do site
#     # será usado a funcão COOKIES.get() para obter o cookie de visitas.
#     # se o cookie existe, o valor retornado é fundido em um inteiro
#     # se o cookie não existe, então o valor default 1 é usado.
#     visits = int(request.COOKIES.get('visits', '1'))
#
#     last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
#     last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
#
#     # se tiver passado mais de um dia desde a ultima visita
#     if (datetime.now() - last_visit_time).days > 0:
#         visits = visits + 1
#         # atualiza o cookie de ultima visita agora que o contador foi atualizado
#         response.set_cookie('last_visit', str(datetime.now()))
#     else:
#         visits = 1
#         # seta o cookie last visit
#         response.set_cookie('last_visit', last_visit_cookie)
#
#     # atualiza/seta o cookie visits
#     response.set_cookie('visits', visits)

def show_category(request, category_name_slug):
    """Cria um dicionario de contexto que será passado para o template"""
    context_dict = {}

    try:
        # Se o nome slug de uma categoria não for encontrada o método .get() devolve uma exceção DoesNotExist
        # Se o nome slug for encontrado o método .get() retorna a instância de um model ou a exceção
        category = Category.objects.get(slug=category_name_slug)

        pages = Page.objects.filter(category=category).order_by('-views')

        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        # Se nenhuma categoria for encontrada o template irá mostrar uma mensagem 'no category'
        context_dict['category'] = None
        context_dict['pages'] = None

    # novo código adicionado para lidar com a requisicao POST
    context_dict['query'] = category.name

    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # roda a função BING para obter a lista de resultados
            result_list = run_query(query)
            context_dict['query'] = query
            context_dict['result_list'] = result_list

    return render(request, 'rango/category.html', context_dict)


@login_required
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


@login_required
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


# def register(request):
#     # Um valor booleano para dizer ao template se o registro teve sucesso.
#     # Definido como False inicialmente. O código altera o valor para True quando o registro for cadastrado.
#     registered = False
#
#     if request.method == 'POST':
#         user_form = UserForm(data=request.POST)
#         profile_form = UserProfileForm(data=request.POST)
#
#         if user_form.is_valid() and profile_form.is_valid():
#             user = user_form.save()
#             # agora será realizado o hash do password com o método set_password
#             # após o hash, o objeto user é atualizado
#             user.set_password(user.password)
#             user.save()
#
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             # se o usuário forneceu uma imagem de profile, então é necessário pegar do input form e coloca-la
#             # no model UserProfile
#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']
#
#             profile.save()
#             # atualiza a variavel registered para indicar que o template de registro teve sucesso.
#             registered = True
#         else:
#             # imprimir possiveis erros no terminal
#             print (user_form.errors, profile_form.errors)
#     else:
#         user_form = UserForm()
#         profile_form = UserProfileForm()
#
#     return render(request, 'rango/register.html', {'user_form': user_form,
#                                                    'profile_form': profile_form,
#                                                    'registered': registered})


# def user_login(request):
#     if request.method == 'POST':
#         # É utilizado request.POST.get('variable') em vez de request.POST['variable']
#         # porque request.POST.get('variable') retorna None se o valor não existir, enquanto request.POST['variable']
#         # implicará em um erro de exceção KeyError
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         user = authenticate(username=username, password=password)
#
#         if user:
#             if user.is_active:
#                 login(request, user)
#                 return HttpResponseRedirect(reverse('index'))
#             else:
#                 return HttpResponse("Your Rango account is disabled")
#         else:
#             print ("Invalid login details: {0}, {1}".format(username, password))
#             return HttpResponse("Invalid login details supplied")
#
#     else:
#         return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


# @login_required
# def user_logout(request):
#     logout(request)
#     return HttpResponseRedirect(reverse('index'))


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect('index')
        else:
            print form.errors

    context_dict = {'form': form}

    return render(request, 'rango/profile_registration.html', context_dict)


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('index')

    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm({'website': userprofile.website, 'picture': userprofile.picture})

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('index')
        else:
            print form.errors

    return render(request, 'rango/profile.html', {'userprofile': userprofile, 'selecteduser': user, 'form': form})


@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()

    return render(request, 'rango/list_profiles.html', {'userprofile_list': userprofile_list})


@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        likes = 0
        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()
        return HttpResponse(likes)

def search(request):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # roda a função BING para obter a lista de resultados
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):
    page_id = None
    url = '/rango/'

    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    return cat_list


def suggest_category(request):
    cat_list = []
    starts_with = ''

    if request.method == 'GET':
        starts_with = request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)

    return render(request, 'rango/cats.html', {'cats': cat_list})


@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}

    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']

        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')
            context_dict['pages'] = pages

    return render(request, 'rango/page_list.html', context_dict)