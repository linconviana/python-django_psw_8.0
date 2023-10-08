from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import TiposExames, PedidosExames, SolicitacaoExame, AcessoMedico
from datetime import date, datetime

# Create your views here.
'@login_required'
def solicitar_exames(request):

    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa fazer login para acessar esta pagina!')
        return redirect('/usuarios/login') 
    
    tipos_exames = TiposExames.objects.all()

    if request.method == 'GET':      
        return render(request, 'solicitar_exames.html', {'tipos_exames' : tipos_exames})
    elif request.method == 'POST':
        exames_id = request.POST.getlist('exames')
        solicitacao_exames = TiposExames.objects.filter(id__in = exames_id)
        
        total_preco = 0
        for i in solicitacao_exames:
            if i.disponivel:
                total_preco += i.preco

        data_atual = date.today()
        data_formatada = data_atual.strftime('%d/%m/%Y')

        return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames, 
                                                         'solicitacao_exames': solicitacao_exames,
                                                         'total_preco': total_preco,
                                                         'data_formatada': data_formatada})

'@login_required'
def fechar_pedido(request):

    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa fazer login para acessar esta pagina!')
        return redirect('/usuarios/login') 
    
    exames_id = request.POST.getlist('exames')
    solicitacao_exames = TiposExames.objects.filter(id__in = exames_id)

    pedido_exame = PedidosExames(
        usuario = request.user,
        data = datetime.now()
    )
    pedido_exame.save()

    for exame in solicitacao_exames:
        solicitacao_exames_temp = SolicitacaoExame(
            usuario = request.user,
            exame = exame,
            status = 'E'
        )
        solicitacao_exames_temp.save()
        pedido_exame.exames.add(solicitacao_exames_temp)

    pedido_exame.save()

    messages.add_message(request, constants.SUCCESS, 'Pedido cadastrado com sucesso!')
    return redirect('/exames/gerenciar_pedidos') 

'@login_required'
def gerenciar_pedidos(request):

    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa fazer login para acessar esta pagina!')
        return redirect('/usuarios/login') 
    
    pedidos_exames = PedidosExames.objects.filter(usuario=request.user)
    return render(request, 'gerenciar_pedidos.html', {'pedidos_exames': pedidos_exames})

'@login_required'
def cancelar_pedido(request, id):

    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa fazer login para acessar esta pagina!')
        return redirect('/usuarios/login')
    
    pedido = PedidosExames.objects.get(id = id)

    if pedido.usuario == request.user:
        pedido.agendado = False
        pedido.save()
    else:
        messages.add_message(request, constants.ERROR, 'Você não tem permissão para cancelar este pedido!')
        return redirect('/exames/gerenciar_pedidos/')

    messages.add_message(request, constants.SUCCESS, 'Pedido cancelado com sucesso!')
    return redirect('/exames/gerenciar_pedidos/')

'@login_required'
def gerenciar_exames(request):

    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa fazer login para acessar esta pagina!')
        return redirect('/usuarios/login')
    
    exames = SolicitacaoExame.objects.filter(usuario=request.user)

    return render(request, 'gerenciar_exames.html', {'exames': exames})

'@login_required'
def permitir_abrir_exame(request, id):

    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa fazer login para acessar esta pagina!')
        return redirect('/usuarios/login')
    
    exame = SolicitacaoExame.objects.get(id = id)
    if not exame.requer_senha:
        return redirect(exame.resultado.url)
    
    return redirect(f'/exames/solicitar_senha_exame/{exame.id}')

'@login_required'
def solicitar_senha_exame(request, id):

    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa fazer login para acessar esta pagina!')
        return redirect('/usuarios/login')
    
    exame = SolicitacaoExame.objects.get(id=id)
    if request.method == "GET":
        return render(request, 'solicitar_senha_exame.html', {'exame': exame})
    elif request.method == "POST":
        senha = request.POST.get("senha")

        if senha == exame.senha:
            return redirect(exame.resultado.url)
        else:
            messages.add_message(request, constants.ERROR, 'Senha inválida')
            return redirect(f'/exames/solicitar_senha_exame/{exame.id}')
'@login_required'        
def gerar_acesso_medico(request):

    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa fazer login para acessar esta pagina!')
        return redirect('/usuarios/login')
    
    if request.method == "GET":
        acessos_medicos = AcessoMedico.objects.filter(usuario =request. user)
        return render(request, 'gerar_acesso_medico.html', {'acessos_medicos': acessos_medicos})
    elif request.method == "POST":
        identificacao = request.POST.get('identificacao')
        tempo_de_acesso = request.POST.get('tempo_de_acesso')
        data_exame_inicial = request.POST.get("data_exame_inicial")
        data_exame_final = request.POST.get("data_exame_final")

        acesso_medico = AcessoMedico(
            usuario = request.user,
            identificacao = identificacao,
            tempo_de_acesso = tempo_de_acesso,
            data_exames_iniciais = data_exame_inicial,
            data_exames_finais = data_exame_final,
            criado_em = datetime.now()
        )

        acesso_medico.save()

        messages.add_message(request, constants.SUCCESS, 'Acesso gerado com sucesso')
        return redirect('/exames/gerar_acesso_medico')

'@login_required'  
def acesso_medico(request, token):

    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa fazer login para acessar esta pagina!')
        return redirect('/usuarios/login')
    
    acesso_medico = AcessoMedico.objects.get(token = token)

    if acesso_medico.status == 'Expirado':
        messages.add_message(request, constants.WARNING, 'Esse link já se expirou!')
        return redirect('/usuarios/login')

    pedidos = PedidosExames.objects.filter(data__gte = acesso_medico.data_exames_iniciais).filter(data__lte = acesso_medico.data_exames_finais).filter(usuario=acesso_medico.usuario)

    return render(request, 'acesso_medico.html', {'pedidos': pedidos})

    