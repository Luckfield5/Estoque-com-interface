from django.contrib import admin
from .models import Produto, Movimentacao

from django.contrib import admin
from .models import Produto, Movimentacao

admin.site.site_header = 'Administração do Painel'
admin.site.site_title = 'Painel de Estoque'
admin.site.index_title = 'Administração do painel'

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sku', 'preco', 'quantidade', 'estoque_minimo', 'ativo')
    search_fields = ('nome', 'sku')
    list_filter = ('ativo',)


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'produto', 'tipo', 'quantidade', 'usuario')
    list_filter = ('tipo',)
    exclude = ('usuario',)

    def save_model(self, request, obj, form, change):
        obj.usuario = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False