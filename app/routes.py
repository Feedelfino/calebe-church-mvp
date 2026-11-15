from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario, MembroFamilia, LancamentoFinanceiro, EventoAgenda, calcular_resumo_mensal

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            return redirect(url_for("main.dashboard"))
        flash("E-mail ou senha inválidos.", "danger")
    return render_template("login.html")

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

@main_bp.route("/dashboard")
@login_required
def dashboard():
    lancamentos = LancamentoFinanceiro.query.order_by(LancamentoFinanceiro.data_lancamento.desc(), LancamentoFinanceiro.id.desc()).all()
    resumo = calcular_resumo_mensal(lancamentos)
    familias = MembroFamilia.query.order_by(MembroFamilia.nome_completo).all()
    return render_template("dashboard.html", lancamentos=lancamentos, resumo=resumo, familias=familias, hoje=date.today().isoformat())

@main_bp.route("/lancamentos/novo", methods=["POST"])
@login_required
def novo_lancamento():
    tipo = request.form.get("tipo", "Entrada")
    categoria = request.form.get("categoria", "Oferta")
    valor = float(request.form.get("valor") or 0)
    qtd_cestas = int(request.form.get("qtd_cestas") or 0)
    descricao = request.form.get("descricao", "").strip()
    data_str = request.form.get("data_lancamento")
    beneficiado_id = request.form.get("id_pessoa_beneficiada")

    if not descricao or (valor <= 0 and qtd_cestas <= 0):
        flash("Informe uma descrição e um valor ou quantidade de cestas maior que zero.", "warning")
        return redirect(url_for("main.dashboard"))

    data_lanc = datetime.strptime(data_str, "%Y-%m-%d").date() if data_str else date.today()
    novo = LancamentoFinanceiro(
        tipo=tipo, categoria=categoria, valor=valor, qtd_cestas=qtd_cestas,
        descricao=descricao, data_lancamento=data_lanc, id_usuario=current_user.id,
        id_pessoa_beneficiada=int(beneficiado_id) if beneficiado_id else None,
    )
    db.session.add(novo)
    db.session.commit()
    flash("Lançamento registrado com sucesso!", "success")
    return redirect(url_for("main.dashboard"))

@main_bp.route("/membros", methods=["GET", "POST"])
@login_required
def membros():
    if request.method == "POST":
        nome = request.form.get("nome_completo", "").strip()
        telefone = request.form.get("telefone", "").strip()
        bairro = request.form.get("bairro", "").strip()
        tipo = request.form.get("tipo", "Membro")
        recebe_cesta = request.form.get("recebe_cesta") == "on"
        if nome and telefone and bairro:
            registro = MembroFamilia(nome_completo=nome, telefone=telefone, bairro=bairro, tipo=tipo, recebe_cesta=recebe_cesta)
            db.session.add(registro)
            db.session.commit()
            flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for("main.membros"))

    busca = request.args.get("q", "").strip()
    query = MembroFamilia.query
    if busca:
        query = query.filter(MembroFamilia.nome_completo.ilike(f"%{busca}%"))
    lista = query.order_by(MembroFamilia.nome_completo).all()
    return render_template("membros.html", membros=lista, busca=busca)

@main_bp.route("/agenda", methods=["GET", "POST"])
@login_required
def agenda():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        data_str = request.form.get("data_evento")
        horario = request.form.get("horario", "").strip()
        local = request.form.get("local", "Templo Principal").strip()
        observacoes = request.form.get("observacoes", "").strip()
        if titulo and data_str and horario:
            evento = EventoAgenda(
                titulo=titulo, data_evento=datetime.strptime(data_str, "%Y-%m-%d").date(),
                horario=horario, local=local, observacoes=observacoes,
            )
            db.session.add(evento)
            db.session.commit()
            flash("Evento adicionado à agenda!", "success")
        return redirect(url_for("main.agenda"))

    eventos = EventoAgenda.query.order_by(EventoAgenda.data_evento.asc(), EventoAgenda.horario.asc()).all()
    return render_template("agenda.html", eventos=eventos, hoje=date.today().isoformat())
