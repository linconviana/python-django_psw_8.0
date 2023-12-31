from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate, login

# Create your views here.
def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':

        primeiro_nome = request.POST.get('primeiro_nome')
        ultimo_nome = request.POST.get('ultimo_nome')
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        email = request.POST.get('email')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas informadas não são identicas!')
            return redirect('/usuarios/cadastro')
        if len(senha) < 6:
            messages.add_message(request, constants.WARNING, 'A senha muito fraca. A senha deve ter no minimo 6 digitos!')
            return redirect('/usuarios/cadastro')

        try:
            usuario = User.objects.create_user(
                first_name = primeiro_nome,
                last_name = ultimo_nome,
                username = username,
                email = email,
                password = senha
            ) 
            messages.add_message(request, constants.SUCCESS, 'Usuário cadastrado com sucesso!')
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema, contate o administrador do sistema!')
            return redirect('/usuarios/cadastro') 
        
        return redirect('/usuarios/cadastro')

def login_user(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username = username, password = senha)
        if user:
            login(request, user)
            return redirect('/exames/solicitar_exames') 
        else:
            messages.add_message(request, constants.ERROR, 'Usuario ou Senha inválidos!')
            return redirect('/usuarios/login') 

