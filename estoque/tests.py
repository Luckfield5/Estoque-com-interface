from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Movimentacao, Produto


class RegraDeSaldoTests(TestCase):
    """Testa a regra principal: entrada soma, saída subtrai e saldo nunca fica negativo."""

    def setUp(self):
        self.usuario = User.objects.create_user('operador', password='senha-de-teste-123')
        self.produto = Produto.objects.create(
            nome='Camiseta Preta M', sku='CAM-001',
            preco='49.90', quantidade=10, estoque_minimo=5,
        )

    def movimentar(self, tipo, quantidade):
        return Movimentacao.objects.create(
            produto=self.produto, usuario=self.usuario,
            tipo=tipo, quantidade=quantidade,
        )

    def saldo(self):
        self.produto.refresh_from_db()
        return self.produto.quantidade

    def test_entrada_soma_ao_saldo(self):
        self.movimentar(Movimentacao.ENTRADA, 5)
        self.assertEqual(self.saldo(), 15)

    def test_saida_subtrai_do_saldo(self):
        self.movimentar(Movimentacao.SAIDA, 3)
        self.assertEqual(self.saldo(), 7)

    def test_saida_igual_ao_saldo_zera_o_estoque(self):
        self.movimentar(Movimentacao.SAIDA, 10)
        self.assertEqual(self.saldo(), 0)

    def test_saida_maior_que_o_saldo_e_bloqueada(self):
        with self.assertRaises(ValidationError):
            self.movimentar(Movimentacao.SAIDA, 11)
        self.assertEqual(self.saldo(), 10)
        self.assertEqual(Movimentacao.objects.count(), 0)

    def test_movimentacao_nao_pode_ser_alterada(self):
        mov = self.movimentar(Movimentacao.ENTRADA, 1)
        mov.quantidade = 99
        with self.assertRaises(ValidationError):
            mov.save()
        self.assertEqual(self.saldo(), 11)

    def test_produto_fica_abaixo_do_minimo_apos_saida(self):
        self.assertFalse(self.produto.abaixo_do_minimo)
        self.movimentar(Movimentacao.SAIDA, 6)
        self.produto.refresh_from_db()
        self.assertTrue(self.produto.abaixo_do_minimo)


class PermissoesTests(TestCase):
    """Testa o acesso de cada perfil às telas do sistema."""

    def setUp(self):
        call_command('criar_perfis')
        self.funcionario = User.objects.create_user('func', password='senha-de-teste-123')
        self.funcionario.groups.add(Group.objects.get(name='Funcionário'))
        self.admin = User.objects.create_user('adm', password='senha-de-teste-123')
        self.admin.groups.add(Group.objects.get(name='Administrador'))

    def test_visitante_e_enviado_para_o_login(self):
        resposta = self.client.get(reverse('produtos'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn('/login/', resposta.url)

    def test_funcionario_pode_abrir_a_tela_de_movimentar(self):
        self.client.force_login(self.funcionario)
        resposta = self.client.get(reverse('movimentar'))
        self.assertEqual(resposta.status_code, 200)

    def test_funcionario_nao_pode_cadastrar_produto(self):
        self.client.force_login(self.funcionario)
        resposta = self.client.get(reverse('produto_novo'))
        self.assertEqual(resposta.status_code, 403)

    def test_administrador_cadastra_produto_com_quantidade_inicial(self):
        self.client.force_login(self.admin)
        dados = {
            'nome': 'Bone Azul', 'sku': 'BON-001', 'preco': '39.90',
            'estoque_minimo': 5, 'quantidade_inicial': 10,
        }
        resposta = self.client.post(reverse('produto_novo'), dados)
        self.assertEqual(resposta.status_code, 302)

        produto = Produto.objects.get(sku='BON-001')
        self.assertEqual(produto.quantidade, 10)
        self.assertEqual(Movimentacao.objects.filter(produto=produto).count(), 1)

    def test_sku_repetido_e_recusado(self):
        Produto.objects.create(nome='Caneca', sku='CAN-001', preco='25.00')
        self.client.force_login(self.admin)
        dados = {
            'nome': 'Outra Caneca', 'sku': 'CAN-001', 'preco': '30.00',
            'estoque_minimo': 0, 'quantidade_inicial': 0,
        }
        resposta = self.client.post(reverse('produto_novo'), dados)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Produto.objects.filter(sku='CAN-001').count(), 1)