from django import forms

from .models import Movimentacao, Produto


class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ['produto', 'tipo', 'quantidade']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produto'].queryset = Produto.objects.filter(ativo=True).order_by('nome')
        self.fields['produto'].label_from_instance = (
            lambda p: f"{p.nome} ({p.sku}) - saldo: {p.quantidade}"
        )


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'sku', 'preco', 'estoque_minimo']
        labels = {
            'nome': 'Nome',
            'sku': 'SKU (código)',
            'preco': 'Preço (R$)',
            'estoque_minimo': 'Estoque mínimo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs['class'] = 'form-control'


class ProdutoNovoForm(ProdutoForm):
    quantidade_inicial = forms.IntegerField(
        label='Quantidade inicial', min_value=0, initial=0, required=False,
        help_text='Se maior que zero, registra uma Entrada no histórico.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantidade_inicial'].widget.attrs['class'] = 'form-control'

    def clean_quantidade_inicial(self):
        return self.cleaned_data.get('quantidade_inicial') or 0