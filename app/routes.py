from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario, MembroFamilia, LancamentoFinanceiro, EventoAgenda

main = Blueprint("main", __name__)


def _parse_data(valor_str: str) -> date:
    if not valor_str:
        return date.today()
    try:
        return datetime.strptime(valor_str, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter_by(email=email, ativo=True).first()
        if usuario and usuario.check_senha(senha):
            login_user(usuario)
            return redirect(url_for("main.dashboard"))

        flash("E-mail ou senha inválidos. Verifique suas credenciais e tente novamente.", "danger")
        return redirect(url_for("main.login"))

    return render_template("login.html")


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))


@main.route("/dashboard")
@login_required
def dashboard():
    lancamentos = LancamentoFinanceiro.query.order_by(
        LancamentoFinanceiro.data_movimento.desc(),
        LancamentoFinanceiro.id.desc()
    ).all()

    total_entradas = sum(l.valor for l in lancamentos if l.tipo == "entrada")
    total_saidas = sum(l.valor for l in lancamentos if l.tipo == "saida")
    saldo = total_entradas - total_saidas

    cestas_in = sum(l.quantidade_cestas for l in lancamentos if l.tipo == "entrada")
    cestas_out = sum(l.quantidade_cestas for l in lancamentos if l.tipo == "saida")
    saldo_cestas = cestas_in - cestas_out

    total_membros = MembroFamilia.query.count()
    membros_lista = MembroFamilia.query.order_by(MembroFamilia.nome.asc()).all()

    return render_template(
        "dashboard.html",
        lancamentos=lancamentos,
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        saldo=saldo,
        saldo_cestas=saldo_cestas,
        total_membros=total_membros,
        membros_lista=membros_lista,
        hoje=date.today().isoformat(),
    )


@main.route("/lancamentos/novo", methods=["POST"])
@login_required
def novo_lancamento():
    tipo = request.form.get("tipo", "entrada")
    categoria = request.form.get("categoria", "Oferta de Culto").strip()
    descricao = request.form.get("descricao", "").strip()
    data_mov = _parse_data(request.form.get("data_movimento", ""))

    try:
        valor = float(request.form.get("valor", 0) or 0)
    except ValueError:
        valor = 0.0

    try:
        qtd_cestas = int(request.form.get("quantidade_cestas", 0) or 0)
    except ValueError:
        qtd_cestas = 0

    membro_id_raw = request.form.get("membro_id", "").strip()
    membro_id = int(membro_id_raw) if membro_id_raw.isdigit() else None

    if not descricao:
        flash("Informe uma descrição para o lançamento.", "danger")
        return redirect(url_for("main.dashboard"))

    lancamento = LancamentoFinanceiro(
        tipo=tipo,
        categoria=categoria,
        valor=max(0.0, valor),
        quantidade_cestas=max(0, qtd_cestas),
        data_movimento=data_mov,
        descricao=descricao,
        usuario_id=current_user.id,
        membro_id=membro_id,
    )
    db.session.add(lancamento)
    db.session.commit()
    flash("Lançamento registrado com sucesso!", "success")
    return redirect(url_for("main.dashboard"))


@main.route("/lancamentos/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_lancamento(id: int):
    item = LancamentoFinanceiro.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash("Lançamento removido.", "success")
    return redirect(url_for("main.dashboard"))


@main.route("/membros", methods=["GET", "POST"])
@login_required
def membros():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        bairro = request.form.get("bairro", "").strip()
        vinculo = request.form.get("vinculo", "Membro").strip()
        recebe_cesta = request.form.get("recebe_cesta") == "1"

        if not nome or not telefone:
            flash("Nome e telefone são obrigatórios.", "danger")
            return redirect(url_for("main.membros"))

        novo = MembroFamilia(
            nome=nome,
            telefone=telefone,
            bairro=bairro,
            vinculo=vinculo,
            recebe_cesta=recebe_cesta,
        )
        db.session.add(novo)
        db.session.commit()
        flash("Cadastro salvo com sucesso!", "success")
        return redirect(url_for("main.membros"))

    busca = request.args.get("q", "").strip()
    query = MembroFamilia.query
    if busca:
        query = query.filter(MembroFamilia.nome.ilike(f"%{busca}%"))

    lista_membros = query.order_by(MembroFamilia.nome.asc()).all()
    return render_template("membros.html", membros=lista_membros, busca=busca)


@main.route("/membros/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_membro(id: int):
    membro = MembroFamilia.query.get_or_404(id)
    db.session.delete(membro)
    db.session.commit()
    flash("Cadastro removido.", "success")
    return redirect(url_for("main.membros"))


@main.route("/agenda", methods=["GET", "POST"])
@login_required
def agenda():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        local = request.form.get("local", "Templo Principal").strip()
        data_ev = _parse_data(request.form.get("data_evento", ""))
        horario = request.form.get("horario", "19:30").strip()
        observacoes = request.form.get("observacoes", "").strip()

        if not titulo:
            flash("Informe o título do culto ou evento.", "danger")
            return redirect(url_for("main.agenda"))

        evento = EventoAgenda(
            titulo=titulo,
            local=local or "Templo Principal",
            data_evento=data_ev,
            horario=horario or "19:30",
            observacoes=observacoes,
            usuario_id=current_user.id,
        )
        db.session.add(evento)
        db.session.commit()
        flash("Atividade adicionada à agenda!", "success")
        return redirect(url_for("main.agenda"))

    eventos = EventoAgenda.query.order_by(
        EventoAgenda.data_evento.asc(),
        EventoAgenda.horario.asc()
    ).all()
    return render_template("agenda.html", eventos=eventos, hoje=date.today().isoformat())


@main.route("/agenda/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_evento(id: int):
    evento = EventoAgenda.query.get_or_404(id)
    db.session.delete(evento)
    db.session.commit()
    flash("Evento removido da agenda.", "success")
    return redirect(url_for("main.agenda"))