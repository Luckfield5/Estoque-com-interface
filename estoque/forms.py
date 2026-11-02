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