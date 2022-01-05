import socket  # С помощью этой библиотеки определим, по какому адресу подняли сервер
from flask import Flask, request, render_template, redirect, session  # Подключаем модули backend-микрофреймворка

import database  # Подключаем свой скрипт с функциями взаимодействия с базами данных

# ------------- #
log = open('log.txt', 'w')  # Открываем log.txt в режиме записи
log.write(socket.gethostbyname(
    socket.gethostname()) + ":27015")  # Записываем в файл ip-адрес компа, на котором запускается сервер (27015 это # порт)
log.close()  # Сохраняем и закрываем файл
# ------------- #

# ------------- #
app = Flask(__name__)  # Запускаем приложение
app.config[
    'SECRET_KEY'] = "super_secret_key"  # Это ключ для защиты от подделки межсайтовых запросов, это тут вообще не нужно
app.config['USERS'] = database.login()  # Берём из базы данных Пользователей, записываем в приложение
# ------------- #


@app.errorhandler(404)  # Если ошибка на стороне пользователя
@app.errorhandler(500)  # Или ошибка на стороне сервера
def error_handler(e):  # Запускаем страницу обработчика ошибок
    return "<h2>Что-то пошло не так</h2><a href='/main'><button>Назад к известности</button></a>"


@app.route('/', methods=['POST', 'GET'])  # Страница авторизации
def login():
    if request.method == 'GET':  # Просто получаем страницу
        if session.get('is_auth'):  # Если мы авторизованы то редирект на страницу пользоавателя
            return redirect("/userpage")
        return render_template("login.html", error_alert="")
    elif request.method == 'POST':  # Посылаем Логин и Пароль через форму
        username = request.form.get('username')
        password = request.form.get('password')
        # print(username, password)  # Эта строчка использовалась во время разработки и полезна при отладке
        if username and password \
                and username in set(app.config["USERS"].keys()) \
                and password in [str(i[1]) for i in app.config["USERS"].values()] \
                and password == app.config["USERS"][username][-1]:  # Проверяем логин и пароль на Валидность
            session["is_auth"] = True  # Если проверка прошла то говорим что пользователь авторизован
            session["user_id"] = int(app.config["USERS"][username][0])  # id авторизованного пользователя тоже запомним
            return redirect("/main")  # Переадресуем уже авторизованого пользователя на главную
        else:  # Если логин и пароль проверку не прошли то загружаем ту же страницу, но с сообщением об ошибке
            return render_template("login.html", error_alert="Неверный логин и/или пароль")


@app.route('/main')  # главная страница
def main_page():
    if not session.get('user_id'): #  Если пользователь не регестрировался то у него нет id и действия на сайте не будут работать, поэтому дадим ему нулевой id
        session["user_id"] = 0
    if not session.get('is_auth'):
        userpage = "Авторизоваться"  # Если не авторизованы, в правом верхнем углу будет эта надпись
    else:
        userpage = "Моя страница"  # Иначе эта
    return render_template("index.html", a=userpage)


@app.route("/squads/<int:squad>")  # Переход на страницу Отряда
def squad_page(squad):
    squad_num, squad_name, squad_slogan, achivements = database.squads(squad)
    # Получаем из базы данных информацию об отряде, на который перешли, вставляем в страницу
    return render_template("squadpage.html",
                           squad_num=squad_num,
                           squad_name=squad_name,
                           squad_slogan=squad_slogan,
                           achivements=achivements,
                           info=database.squad_info(squad),
                           admin=("admin" in database.userinfo(session.get('user_id'))["post"] and session.get(
                               'is_auth')), )


@app.route("/userpage")  # Страница пользователя
def userpage():
    if not session.get('is_auth'):  # Если ты не авторизован то иди авторизуйся
        return redirect("/")
    pioneer_post = ''
    userInfo = database.userinfo(session.get('user_id'))  # Пишем в userInfo информацию о пользователе, взятому из базы данных по id
    if userInfo["post"] not in (None, ''):  # Должность пишем только для того, у кого она есть
        pioneer_post = f"Должность: {userInfo['post']}"
    return render_template("userpage.html",
                           name=userInfo["name"],
                           firstname=userInfo["firstname"],
                           lastname=userInfo["lastname"],
                           squad=userInfo["squad"],
                           balance=userInfo["balance"],
                           post=pioneer_post, info=database.check_fines(session.get('user_id')))


@app.route("/logout/")  # Сюда мы переадресуем пользователя, решившего выйти из аккаунта
def logout():
    session["is_auth"] = False  # Тут делаем пользователя неавторизованным
    return redirect("/")  # И переадресуем его на страницу авторизации


@app.route("/edit/<int:id>", methods=['POST', 'GET'])
# Сюда мы переадресуем пользователя-админа для редактирования пользователя
# (кнопка edit в таблицах отряда хранит id пользователя, которого она редактирует)
def edit_user(id):  # Передаём id редактируемого пользователя

    # -- см. комментарии userPage -- #
    pioneer_post = ''
    userInfo = database.userinfo(id)
    if userInfo["post"] != 'pioner':
        pioneer_post = f"Должность: {userInfo['post']}"
    if request.method == 'GET':
        if not (session.get('is_auth') and ("admin" in database.userinfo(session.get('user_id'))["post"])):
            return redirect("/main")
        return render_template("edit_user.html",
                               id=userInfo["id"],
                               name=userInfo["name"],
                               firstname=userInfo["firstname"],
                               lastname=userInfo["lastname"],
                               squad=userInfo["squad"],
                               balance=userInfo["balance"],
                               post=pioneer_post,
                               error_alert='',
                               info=database.check_fines(id))
    # ----------------------------- #

    # Работа с Формой штрафа/премирования #
    elif request.method == 'POST':
        fine = request.form.get('fine')
        tal = request.form.get('sum')
        comm = request.form.get('comment')
        if tal and comm and str(tal).isdigit():
            if fine:
                tal = -int(tal)
            database.change_balance(id, int(tal), comm)
            print(database.check_fines(id))
            tal = comm = ''
            return redirect(f"/edit/{id}")
        else:
            return render_template("edit_user.html",
                                   id=userInfo["id"],
                                   name=userInfo["name"],
                                   firstname=userInfo["firstname"],
                                   lastname=userInfo["lastname"],
                                   squad=userInfo["squad"],
                                   balance=userInfo["balance"],
                                   post=pioneer_post,
                                   error_alert='Неверный формат данных', info=database.check_fines(id))


@app.route("/change/<squad>/<digit>")  # Сюда мы переходим при нажатии кнопки Увеличения и Уменьшения количества побед в мероприятиях
def change(squad, digit):
    if not (session.get('is_auth') and ("admin" in database.userinfo(session.get('user_id'))["post"])):
        pass  # Если сюда пытается перейти не_админ то ничего не изменится
    else:  # Если ты админ, то всё меняется соответствующе нажатой кнопке
        if digit == '+':
            database.change_achivements(squad, 1)
        elif digit == '-':
            database.change_achivements(squad, -1)
    return redirect(f"/squads/{squad}")


if __name__ == '__main__':
    app.run(host=socket.gethostbyname(socket.gethostname()), port=27015)
    # app.run(host='127.0.0.1', port=8000)  # раскомменть для дебага
