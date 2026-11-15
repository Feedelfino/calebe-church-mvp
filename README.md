# MVP da Calebe Church

Sistema web responsivo desenvolvido para centralizar a gestão administrativa, financeira e assistencial da **Calebe Church** (Barueri - SP), substituindo planilhas isoladas e controles manuais por um painel único, simples e acessível pelo computador da secretaria e pelo celular dos líderes.

## Problema Resolvido e Impacto (ODS 16)
Atualmente, o controle de dízimos, ofertas, doações de cestas básicas, cadastro de membros/famílias e agenda mensal da igreja fica espalhado em planilhas separadas e anotações manuais. Este MVP unifica esses três módulos em uma interface leve e intuitiva, fortalecendo a organização interna e a transparência na prestação de contas (**ODS 16 — Paz, Justiça e Instituições Eficazes**)[cite: 5].

## Funcionalidades do MVP
- **Autenticação Segura (RF01):** Login restrito para o Pastor Presidente e voluntários autorizados, com senhas protegidas por hash criptográfico (`Werkzeug Security`)[cite: 5].
- **Cadastro de Membros e Famílias (RF02):** Registro, consulta e filtro de membros da igreja e famílias acompanhadas na distribuição de cestas básicas[cite: 5].
- **Controle Financeiro e Doações (RF03 / RF04):** Lançamento de entradas e saídas (dízimos, ofertas, doações e cestas básicas) com cálculo automático do balanço mensal[cite: 5].
- **Agenda Mensal (RF05):** Organização cronológica de cultos, reuniões e entregas sociais[cite: 5].

## Arquitetura e Tecnologias
O projeto segue a **Arquitetura Monolítica em Camadas (padrão MVC)**, separando apresentação, regras de negócio e persistência[cite: 5]:
- **Linguagem e Framework:** Python 3.12 + Flask 3.1[cite: 5]
- **Interface Responsiva (View):** Jinja2 + Bootstrap 5.3[cite: 5]
- **Persistência (Model):** Flask-SQLAlchemy 3.1 (SQLite em ambiente local / PostgreSQL em produção)[cite: 5]
- **Segurança:** Flask-Login 0.6 + Werkzeug Security[cite: 5]
- **Testes e CI:** Pytest + GitHub Actions

## Como Executar o Projeto Localmente

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/Feedelfino/calebe-church-mvp.git](https://github.com/Feedelfino/calebe-church-mvp.git)
   cd calebe-church-mvphttps://github.com/Feedelfino/calebe-church-mvp
   
   
2. **Crie e ative o ambiente virtual:**

    * Windows (PowerShell/CMD): python -m venv venv e depois venv\Scripts\activate

    * Linux/Mac: python3 -m venv venv e depois source venv/bin/activate

3. **Instale as dependências:** pip install -r requirements.txt

4. **Execute a aplicação:python run.py**
Acesse no navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)