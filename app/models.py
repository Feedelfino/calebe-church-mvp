from datetime import date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    perfil = db.Column(db.String(30), nullable=False, default="voluntario")

    def definir_senha(self, senha_plana: str) -> None:
        self.senha_hash = generate_password_hash(senha_plana)

    def verificar_senha(self, senha_plana: str) -> bool:
        return check_password_hash(self.senha_hash, senha_plana)

    @staticmethod
    def criar_admin_padrao() -> None:
        if not Usuario.query.filter_by(email="pastor@calebechurch.org").first():
            admin = Usuario(nome="Pastor Ricardo", email="pastor@calebechurch.org", perfil="admin")
            admin.definir_senha("calebe2026")
            db.session.add(admin)
            db.session.commit()

class MembroFamilia(db.Model):
    __tablename__ = "membros_familias"
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(25), nullable=False)
    bairro = db.Column(db.String(80), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default="Membro")
    recebe_cesta = db.Column(db.Boolean, default=False)

class LancamentoFinanceiro(db.Model):
    __tablename__ = "lancamentos_financeiros"
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(15), nullable=False)
    categoria = db.Column(db.String(40), nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)
    qtd_cestas = db.Column(db.Integer, nullable=False, default=0)
    descricao = db.Column(db.String(200), nullable=False)
    data_lancamento = db.Column(db.Date, nullable=False, default=date.today)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    id_pessoa_beneficiada = db.Column(db.Integer, db.ForeignKey("membros_familias.id"), nullable=True)

class EventoAgenda(db.Model):
    __tablename__ = "eventos_agenda"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    data_evento = db.Column(db.Date, nullable=False)
    horario = db.Column(db.String(10), nullable=False)
    local = db.Column(db.String(100), nullable=False, default="Templo Principal")
    observacoes = db.Column(db.String(200), nullable=True)

def calcular_resumo_mensal(lancamentos):
    entradas = sum(l.valor for l in lancamentos if l.tipo == "Entrada")
    saidas = sum(l.valor for l in lancamentos if l.tipo == "Saida")
    cestas_entradas = sum(l.qtd_cestas for l in lancamentos if l.tipo == "Entrada")
    cestas_entregues = sum(l.qtd_cestas for l in lancamentos if l.tipo == "Saida")
    return {
        "entradas": round(entradas, 2),
        "saidas": round(saidas, 2),
        "saldo": round(entradas - saidas, 2),
        "cestas_disponiveis": cestas_entradas - cestas_entregues,
    }
