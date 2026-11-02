from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

PERFIS = {
    'Funcionário': [
        'view_produto',
        'view_movimentacao',
        'add_movimentacao',
    ],
    'Administrador': [
        'view_produto', 'add_produto', 'change_produto', 'delete_produto',
        'view_movimentacao', 'add_movimentacao',
        'view_user', 'add_user', 'change_user',
    ],
}


class Command(BaseCommand):
    help = 'Cria os grupos Funcionário e Administrador com suas permissões'

    def handle(self, *args, **options):
        for nome, codigos in PERFIS.items():
            grupo, _ = Group.objects.get_or_create(name=nome)
            permissoes = Permission.objects.filter(codename__in=codigos)
            grupo.permissions.set(permissoes)
            self.stdout.write(self.style.SUCCESS(
                f'{nome}: {permissoes.count()} permissões'
            ))