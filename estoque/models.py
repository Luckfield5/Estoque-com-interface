from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction


class Produto(models.Model):
    nome = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, unique=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    quantidade = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return f"{self.nome} ({self.sku})"

    @property
    def abaixo_do_minimo(self):
        return self.quantidade < self.estoque_minimo


class Movimentacao(models.Model):
    ENTRADA = 'ENTRADA'
    SAIDA = 'SAIDA'
    TIPOS = [(ENTRADA, 'Entrada'), (SAIDA, 'Saída')]

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    data_hora = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'

    def __str__(self):
        return f"{self.tipo} {self.quantidade} - {self.produto.nome}"

    def clean(self):
        if self.produto_id and self.tipo == self.SAIDA and self.quantidade:
            if self.quantidade > self.produto.quantidade:
                raise ValidationError(
                    f"Saldo insuficiente: o estoque tem {self.produto.quantidade} unidade(s)."
                )

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Movimentações não podem ser alteradas.")
        with transaction.atomic():
            produto = Produto.objects.select_for_update().get(pk=self.produto_id)
            if self.tipo == self.SAIDA:
                if self.quantidade > produto.quantidade:
                    raise ValidationError("Saldo insuficiente em estoque.")
                produto.quantidade -= self.quantidade
            else:
                produto.quantidade += self.quantidade
            produto.save()
            super().save(*args, **kwargs)