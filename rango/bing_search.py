# -*- coding: utf-8 -*-

import json
import urllib, urllib2


def read_bing_key():
    """
    Lê a chave BING API de um arquivo chamado bing.key
    :return: uma string que pode ser NONE se a chave não for encontrada, ou o valor da chave
    """
    bing_api_key = None

    try:
        with open('bing.key', 'r') as f:
            bing_api_key = f.readline()
    except:
        raise IOError('bing.key file not found')

    return bing_api_key


def run_query(search_terms):
    """
    Entrega uma string contendo os termos busca (query),
    :param search_terms:
    :return: retorna uma lista com os resultados do engine de busca do Bing
    """
    bing_api_key = read_bing_key()

    if not bing_api_key:
        raise KeyError("Bing key not found")

    # especifica a url base e os serviços (BING SEARCH API 2.0)
    root_url = 'https://api.datamarket.azure.com/bing/Search/'
    service = 'Web'

    # especifica quantos resultados será retornado por página
    # offset especifica onde a lista dos resultados inicia
    # com results_per_page = 10 and offset = 11, irá iniciar na página 2
    results_per_page = 10
    offset = 0

    # colocar aspas em volta dos termos da query exigido pela API Bing
    # a query será então armazenada em uma variável
    query = "'{0}'".format(search_terms)

    # transforma a query em uma string HTML codificada usando urllib
    # We use urllib for this - differences exist between Python 2 and 3.
    # The try/except blocks are used to determine which function call works.
    # Replace this try/except block with the relevant import and query assignment.
    try:
        from urllib import parse  # Python 3 import.
        query = parse.quote(query)
    except ImportError:  # If the import above fails, you are running Python 2.7.x.
        from urllib import quote
        query = quote(query)

    # contrói a última parte da requisição URL
    # seta o formato da resposta para JSON e seta outra propriedades
    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
        root_url, service, results_per_page, offset, query)

    # configura autenticação com os servidores BING
    # o nome de usuario PRECISA ser uma string em branco
    username = ''

    # configura o gerenciador de password para ajudar a autenticar a requisicao
    try:
        from urllib import request  # Python 3 import.
        password_mgr = request.HTTPPasswordMgrWithDefaultRealm()
    except ImportError:  # Running Python 2.7.x - import urllib2 instead.
        import urllib2
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

    password_mgr.add_password(None, search_url, username, bing_api_key)

    # cria a lista com os resultados
    results = []

    try:
        # prepara para conectar com os sevidores Bing
        try:  # Python 3.5 and 3.6
            handler = request.HTTPBasicAuthHandler(password_mgr)
            opener = request.build_opener(handler)
            request.install_opener(opener)
        except UnboundLocalError:  # Python 2.7.x
            handler = urllib2.HTTPBasicAuthHandler(password_mgr)
            opener = urllib2.build_opener(handler)
            urllib2.install_opener(opener)

        # conecta com o servidor e le a resposta gerada
        try:  # Python 3.5 or 3.6
            response = request.urlopen(search_url).read()
            response = response.decode('utf-8')
        except UnboundLocalError:  # Python 2.7.x
            response = urllib2.urlopen(search_url).read()

        # converte a string de resposta em um dicionario Python
        json_response = json.loads(response)

        # laço através de cada página retornada, populando a lista de resultados
        for result in json_response['d']['results']:
            results.append({'title': result['Title'],
                            'link': result['Url'],
                            'summary': result['Description']})
    except:
        print ("Error when querying the BING API")

    # retorna a lista de resultados para a função que chamou
    return results