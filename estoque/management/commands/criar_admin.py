import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria ou atualiza o superusuário a partir de variáveis de ambiente'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', '')

        if not username or not password:
            self.stdout.write('Variáveis DJANGO_SUPERUSER_USERNAME e DJANGO_SUPERUSER_PASSWORD ausentes: nada a fazer.')
            return

        User = get_user_model()
        user, criado = User.objects.get_or_create(username=username)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        situacao = 'criado' if criado else 'atualizado'
        self.stdout.write(self.style.SUCCESS(f'Superusuário {username} {situacao}.'))