import os
import sys
from datetime import date
import pytest

# Garante que a pasta raiz (onde esta o pacote 'app') seja sempre encontrada
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import (
    Usuario,
    MembroFamilia,
    LancamentoFinanceiro,
    EventoAgenda,
    calcular_resumo_mensal,
)


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_calculo_resumo_mensal_unitario():
    """Teste unitario (AAA): verifica soma de entradas, saidas, saldo e cestas."""
    lancamentos = [
        LancamentoFinanceiro(tipo="Entrada", categoria="Dizimo", valor=500.0, qtd_cestas=0, descricao="Dizimo"),
        LancamentoFinanceiro(tipo="Entrada", categoria="Cesta Basica", valor=0.0, qtd_cestas=10, descricao="Doacao cestas"),
        LancamentoFinanceiro(tipo="Saida", categoria="Oferta", valor=150.5, qtd_cestas=0, descricao="Conta luz"),
        LancamentoFinanceiro(tipo="Saida", categoria="Cesta Basica", valor=0.0, qtd_cestas=3, descricao="Entrega familia"),
    ]
    resumo = calcular_resumo_mensal(lancamentos)

    assert resumo["entradas"] == 500.00
    assert resumo["saidas"] == 150.50
    assert resumo["saldo"] == 349.50
    assert resumo["cestas_disponiveis"] == 7


def test_hash_senha_usuario():
    """Teste unitario: garante que senha nunca fica em texto plano."""
    user = Usuario(nome="Secretaria", email="sec@calebechurch.org")
    user.definir_senha("senhaSegura123")

    assert user.senha_hash != "senhaSegura123"
    assert user.verificar_senha("senhaSegura123") is True
    assert user.verificar_senha("senhaErrada") is False


def test_fluxo_integracao_login_e_lancamento(client):
    """Teste de integracao: login do Pastor Ricardo e registro de lancamento financeiro."""
    resp_login = client.post(
        "/login",
        data={"email": "pastor@calebechurch.org", "senha": "calebe2026"},
        follow_redirects=True,
    )
    assert resp_login.status_code == 200
    assert b"Painel Financeiro" in resp_login.data

    resp_lanc = client.post(
        "/lancamentos/novo",
        data={
            "tipo": "Entrada",
            "categoria": "Oferta",
            "valor": "250.00",
            "qtd_cestas": "2",
            "descricao": "Oferta culto de domingo",
            "data_lancamento": date.today().isoformat(),
        },
        follow_redirects=True,
    )
    assert resp_lanc.status_code == 200
    assert b"Oferta culto de domingo" in resp_lanc.data
    assert b"250.00" in resp_lanc.data


def test_fluxo_integracao_membros_e_agenda(client):
    """Teste de integracao: cadastro de familia assistida e agendamento de culto."""
    client.post(
        "/login",
        data={"email": "pastor@calebechurch.org", "senha": "calebe2026"},
    )

    resp_membro = client.post(
        "/membros",
        data={
            "nome_completo": "Familia Silva",
            "telefone": "(11) 98888-7777",
            "bairro": "Jardim Belval",
            "tipo": "Familia",
            "recebe_cesta": "on",
        },
        follow_redirects=True,
    )
    assert resp_membro.status_code == 200
    assert b"Familia Silva" in resp_membro.data

    resp_agenda = client.post(
        "/agenda",
        data={
            "titulo": "Culto de Celebracao",
            "data_evento": date.today().isoformat(),
            "horario": "19:30",
            "local": "Templo Principal",
        },
        follow_redirects=True,
    )
    assert resp_agenda.status_code == 200
    assert b"Culto de Celebracao" in resp_agenda.data