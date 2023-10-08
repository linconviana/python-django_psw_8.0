from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.contrib.auth.models import User
from django.db.models import Value
from django.db.models.functions import Concat
from django.contrib.admin.views.decorators import staff_member_required
from exames.models import SolicitacaoExame
from .utils import gerar_pdf_exames, gerar_senha_aleatoria
from django.contrib.messages import constants
from django.contrib import messages

@staff_member_required 
def gerenciar_clientes(request):
    clientes = User.objects.filter(is_staff=False)

    nome_completo = request.GET.get('nome')
    email = request.GET.get('email')

    if email:
        clientes = clientes.filter(email__contains = email)
    if nome_completo:
        clientes = clientes.annotate(
            full_name=Concat('first_name', Value(' '), 'last_name')
        ).filter(full_name__contains=nome_completo)

    return render(request, 'gerenciar_clientes.html', {'clientes': clientes, 'nome_completo': nome_completo, 'email': email})

@staff_member_required 
def cliente(request, id):
    cliente = User.objects.get(id=id)
    exames = SolicitacaoExame.objects.filter(usuario=cliente)
    return render(request, 'cliente.html', {'cliente': cliente, 'exames': exames})

@staff_member_required 
def exame_cliente(request, id):
    exame = SolicitacaoExame.objects.get(id=id)
    return render(request, 'exame_cliente.html', {'exame': exame})

@staff_member_required 
def proxy_pdf(request, id):
    exame = SolicitacaoExame.objects.get(id=id)

    response = exame.resultado.open()
    return FileResponse(response)

@staff_member_required 
def gerar_senha(request, id):
    exame = SolicitacaoExame.objects.get(id=id)

    if exame.senha:
        return FileResponse(gerar_pdf_exames(exame.exame.nome, exame.usuario, exame.senha), filename="token.pdf")
    
    senha = gerar_senha_aleatoria(9)
    exame.senha = senha
    exame.save()
    return FileResponse(gerar_pdf_exames(exame.exame.nome, exame.usuario, exame.senha), filename="token.pdf")

@staff_member_required 
def alterar_dados_exame(request, id):
    exame = SolicitacaoExame.objects.get(id=id)

    pdf = request.FILES.get('resultado')
    status = request.POST.get('status')
    requer_senha = request.POST.get('requer_senha')
    
    if requer_senha and (not exame.senha):
        messages.add_message(request, constants.ERROR, 'Para exigir a senha primeiro crie uma.')
        return redirect(f'/empresarial/exame_cliente/{id}')
    
    exame.requer_senha = True if requer_senha else False

    if pdf:
        exame.resultado = pdf
        
    exame.status = status
    exame.save()
    messages.add_message(request, constants.SUCCESS, 'Alteração realizada com sucesso')
    return redirect(f'/empresarial/exame_cliente/{id}')