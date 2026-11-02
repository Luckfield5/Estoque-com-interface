from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import DecimalField, ExpressionWrapper, F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MovimentacaoForm, ProdutoForm, ProdutoNovoForm
from .models import Movimentacao, Produto


@login_required
def dashboard(request):
    ativos = Produto.objects.filter(ativo=True)
    valor = ativos.aggregate(
        total=Sum(ExpressionWrapper(
            F('preco') * F('quantidade'),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        ))
    )['total'] or 0

    contexto = {
        'total_produtos': ativos.count(),
        'valor_estoque': valor,
        'abaixo_minimo': ativos.filter(quantidade__lt=F('estoque_minimo')),
        'ultimas': Movimentacao.objects.select_related('produto', 'usuario')
                               .order_by('-data_hora')[:8],
    }
    return render(request, 'estoque/dashboard.html', contexto)


@login_required
def produtos(request):
    busca = request.GET.get('q', '').strip()
    lista = Produto.objects.filter(ativo=True).order_by('nome')
    if busca:
        lista = lista.filter(Q(nome__icontains=busca) | Q(sku__icontains=busca))
    return render(request, 'estoque/produtos.html', {'produtos': lista, 'busca': busca})


@login_required
@permission_required('estoque.add_produto', raise_exception=True)
def produto_novo(request):
    form = ProdutoNovoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            produto = form.save(commit=False)
            produto.quantidade = 0
            produto.save()
            inicial = form.cleaned_data['quantidade_inicial']
            if inicial > 0:
                Movimentacao.objects.create(
                    produto=produto,
                    usuario=request.user,
                    tipo=Movimentacao.ENTRADA,
                    quantidade=inicial,
                )
        messages.success(request, 'Produto cadastrado com sucesso.')
        return redirect('produtos')
    return render(request, 'estoque/produto_form.html',
                  {'form': form, 'titulo': 'Novo produto'})


@login_required
@permission_required('estoque.change_produto', raise_exception=True)
def produto_editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk, ativo=True)
    form = ProdutoForm(request.POST or None, instance=produto)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Produto atualizado com sucesso.')
        return redirect('produtos')
    return render(request, 'estoque/produto_form.html',
                  {'form': form, 'titulo': 'Editar produto'})


@login_required
@permission_required('estoque.delete_produto', raise_exception=True)
@require_POST
def produto_desativar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    produto.ativo = False
    produto.save()
    messages.success(request, 'Produto desativado. O histórico foi mantido.')
    return redirect('produtos')


@login_required
@permission_required('estoque.add_movimentacao', raise_exception=True)
def movimentar(request):
    form = MovimentacaoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        mov = form.save(commit=False)
        mov.usuario = request.user
        try:
            mov.save()
        except Exception as erro:
            form.add_error(None, getattr(erro, 'messages', [str(erro)]))
        else:
            messages.success(request, 'Movimentação registrada com sucesso.')
            return redirect('movimentar')
    return render(request, 'estoque/movimentar.html', {'form': form})


@login_required
@permission_required('estoque.view_movimentacao', raise_exception=True)
def historico(request):
    lista = Movimentacao.objects.select_related('produto', 'usuario').order_by('-data_hora')
    tipo = request.GET.get('tipo', '')
    busca = request.GET.get('q', '').strip()
    if tipo in (Movimentacao.ENTRADA, Movimentacao.SAIDA):
        lista = lista.filter(tipo=tipo)
    if busca:
        lista = lista.filter(Q(produto__nome__icontains=busca) | Q(produto__sku__icontains=busca))
    contexto = {
        'movimentacoes': lista[:100],
        'busca': busca,
        'sel_entrada': 'selected' if tipo == Movimentacao.ENTRADA else '',
        'sel_saida': 'selected' if tipo == Movimentacao.SAIDA else '',
    }
    return render(request, 'estoque/historico.html', contexto)