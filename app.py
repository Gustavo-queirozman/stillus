from logging import error
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask.wrappers import Request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
#criar outra base de dados para usuario-admin
#criar painel para editar dados do usuario-admin e ver dados de agendamentos
#criar outra base de dados para usuario-admin
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdjcjkd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def current_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    cell = db.Column(db.String(15), nullable=False)

    def __str__(self):
        return self.name

class Schedule(db.Model):
    __tablename__ = "schedule"
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(255), nullable=False)
    data = db.Column(db.String(15), nullable=False)
    horario = db.Column(db.String(5), nullable=False)
    corte = db.Column(db.String(255), nullable=False)
    def __str__(self):
        return self.horario
        

@app.route('/')
def index():
    #users = User.query.all()  # seleciona todos usuarios do banco de dados
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Credenciais incorretas")
            return redirect(url_for('login'))

        if not check_password_hash(user.password, password):
            flash("Credenciais incorretas")
            return redirect(url_for('login'))

        login_user(user)
        session['id'] = user.id
        session['name']=user.name
        return redirect(url_for('data'))

    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        user = User()
        user.name = request.form['name']
        user.email = request.form['email']
        user.password = generate_password_hash(request.form['password'])
        user.cell = request.form['cell']
        db.session.add(user)
        db.session.commit()
        session['id'] = user.id
        session['name']=user.name
        return redirect(url_for('data'))
    return render_template('cadastro.html')

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if request.method == 'POST':
        user = User.query.get(session['id'])
        user.name = request.form['name']
        user.email = request.form['email']
        user.password = generate_password_hash(request.form['password'])
        user.cell = request.form['cell']
        db.session.commit()
    user = User.query.get(session['id'])
    return render_template('perfil.html', user=user)

@app.route('/data')
def data():
    hours = ['7:00', '7:40', '8:20', '9:00', '9:40', '10:20', '11:00',
             '11:40', '12:20', '14:10', '14:50', '15:30', '16:10', '17:50']
    return render_template('data.html', hours=hours)


@app.route('/agendar', methods=["POST"])
@login_required
def agendar():
    hours = ['7:00', '7:40', '8:20', '9:00', '9:40', '10:20', '11:00',
             '11:40', '12:20', '14:10', '14:50', '15:30', '16:10', '17:50']

    if request.method == "POST":
        date = request.form['date']
        dateFormat = date.replace("-", "/")
        dateFormat= dateFormat[8:10]+dateFormat[4:8]+dateFormat[0:4]
        horarios_agendados = Schedule.query.filter_by(data=dateFormat).all()
        for horario in horarios_agendados:
            hours.remove("{}".format(horario))
    return render_template('agendar.html', hours=hours, date=date)

@app.route('/agendamento', methods=["POST", "GET"])
@login_required
def agendamento():
        date = request.form['date']
        dateFormat = date.replace("-", "/")
        dateFormat= dateFormat[8:10]+dateFormat[4:8]+dateFormat[0:4]
        schedule = Schedule()
        schedule.id = session['id'] 
        schedule.cliente = session['name']
        schedule.data = dateFormat
        schedule.horario = str(request.form.get('select-hour'))
        schedule.corte = str(request.form.get('select-corte'))
        db.session.add(schedule)
        db.session.commit()
        return redirect(url_for('agendado'))

@app.route('/agendado')
@login_required
def agendado():
    user = User.query.get(session['id'])
    name = user.name
    cell = user.cell
    agendado = Schedule.query.get(session['id'])
    corte = agendado.corte
    horario = agendado.horario
    return render_template('agendado.html', cliente=name, contato=cell, horario=horario, corte=corte)

@app.route('/sair')
@login_required
def sair():
    logout_user()
    return redirect('/')

#Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Credenciais incorretas")
            return redirect('/dashboard')

        if not check_password_hash(user.password, password):
            flash("Credenciais incorretas")
            return redirect('/dashboard')

        login_user(user)
        session['id'] = user.id
        session['name']=user.name
        return redirect('/dashboard/painel')

    return render_template('/dashboard/index.html')


@app.route('/dashboard/cadastro', methods=['GET', 'POST'])
def dashcadastro():
    if request.method == 'POST':
        user = User()
        user.name = request.form['name']
        user.email = request.form['email']
        user.password = generate_password_hash(request.form['password'])
        user.cell = request.form['cell']
        db.session.add(user)
        db.session.commit()
        session['id'] = user.id
        session['name']=user.name
        return redirect('/dashboard/painel')
    return render_template('/dashboard/cadastro.html')

@app.route('/dashboard/painel')
def dashpainel():
    return render_template('/dashboard/painel.html')

@app.route('/dashboard/dados', methods=['GET', 'POST'])
def dashdados():
    if request.method == 'POST':
        user = User.query.get(session['id'])
        user.name = request.form['name']
        user.email = request.form['email']
        user.password = generate_password_hash(request.form['password'])
        user.cell = request.form['cell']
        db.session.commit()
    user = User.query.get(session['id'])
    return render_template('/dashboard/dados.html', user=user)

@app.route("/dashboard/agendamentos")
def agendamentos():
    agendamento = Schedule.query.all()
    return render_template('agendamentos.html', agendamento=agendamento) # just to see what select is

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    schedule = Schedule.query.filter_by(id=id).first()
    db.session.delete(schedule)
    db.session.commit()
    return redirect('/dashboard/agendamentos') # just to see what select is

#USUÁRIOS
@app.route("/user")
def users():
    users = User.query.all()
    return render_template('users.html', users=users) # just to see what select is

@app.route("/user/<int:id>")
def deleteUser(id):
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect('/user') # just to see what select is


if __name__ == "__main__":
    app.run(debug=True)
