from datetime import date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    perfil = db.Column(db.String(40), nullable=False, default="administrador")
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    def set_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)


class MembroFamilia(db.Model):
    __tablename__ = "membros_familias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    telefone = db.Column(db.String(40), nullable=False)
    bairro = db.Column(db.String(100), nullable=True)
    vinculo = db.Column(db.String(60), nullable=False, default="Membro")
    recebe_cesta = db.Column(db.Boolean, nullable=False, default=False)
    data_cadastro = db.Column(db.Date, nullable=False, default=date.today)


class LancamentoFinanceiro(db.Model):
    __tablename__ = "lancamentos_financeiros"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'entrada' ou 'saida'
    categoria = db.Column(db.String(80), nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)
    quantidade_cestas = db.Column(db.Integer, nullable=False, default=0)
    data_movimento = db.Column(db.Date, nullable=False, default=date.today)
    descricao = db.Column(db.String(255), nullable=False)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    membro_id = db.Column(db.Integer, db.ForeignKey("membros_familias.id"), nullable=True)
    membro = db.relationship("MembroFamilia", backref="lancamentos")


class EventoAgenda(db.Model):
    __tablename__ = "eventos_agenda"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    data_evento = db.Column(db.Date, nullable=False, default=date.today)
    horario = db.Column(db.String(10), nullable=False, default="19:30")
    local = db.Column(db.String(120), nullable=False, default="Templo Principal")
    observacoes = db.Column(db.String(255), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)