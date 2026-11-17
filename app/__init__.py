import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message = "Faça login para acessar esta página."
login_manager.login_message_category = "danger"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-calebe-church-2026")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///calebe.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import Usuario

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(Usuario, int(user_id))

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(email="secretaria@calebechurch.org.br").first():
            admin = Usuario(
                nome="Pr. Ricardo (Administrador)",
                email="secretaria@calebechurch.org.br",
                perfil="administrador",
                ativo=True,
            )
            admin.set_senha("Calebe@2026")
            db.session.add(admin)
            db.session.commit()

    return app