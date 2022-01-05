import sqlite3  # Имортируем взаимодействие с языком запросов к базе данных


def login():  # Возвращает словарь пользователей вида { "И.Фамилия": (id, "Пароль")}
    db = sqlite3.connect("db/db.db")
    cur = db.cursor()
    users = [elem[0] for elem in cur.execute("""SELECT firstname FROM users ORDER BY firstname""")]
    names = [elem[0][0] for elem in cur.execute("""SELECT name FROM users ORDER BY firstname""")]
    info = list(cur.execute("""SELECT id, password FROM users ORDER BY firstname"""))
    db.close()

    data = dict()
    for i in range(len(users)):
        data[names[i]+'.'+users[i]] = info[i]
    return data


def squads(num):  # Возвращает всю информацию об отряде по номеру вида (Номер, "Название", "Девиз", Кол-во_побед)
    db = sqlite3.connect("db/db.db")
    cur = db.cursor()
    squad_info = list(cur.execute(f"""SELECT * FROM squads WHERE number = {num}"""))[0]
    db.close()
    return squad_info


def userinfo(id):
    # Возвращает информацию о пользователе по id вида
    # { 'id': id, 'name': 'имя', 'firstname': 'фамилия', 'lastname': 'отчество', 'password': 'пароль', 'squad': отряд,
    # 'balance': баланс, 'post': 'должность'}
    db = sqlite3.connect("db/db.db")
    cur = db.cursor()
    users = list(cur.execute(f"""SELECT * FROM users WHERE id = {id}"""))[0]
    db.close()
    keys = ('id', 'name', 'firstname', 'lastname', 'password', 'squad', 'balance', 'post')
    data = dict()
    for i in range(len(users)):
        data[keys[i]] = users[i]
    return data


def squad_info(squad):  # Возвращает информацию вида ('Фамилия', 'Имя', 'Отчество', баланс, id) обо всех пользователях из выбранного отряда
    db = sqlite3.connect("db/db.db")
    cur = db.cursor()
    pioners = list(cur.execute(f"""SELECT firstname, name, post, balance, id FROM users WHERE squad = {squad}"""))
    db.close()
    return pioners


def change_balance(id, sum, comment):  # Меняет пользователю, выбранному по id баланс на sum, с комментарием comment
    db = sqlite3.connect("db/db.db")
    cur = db.cursor()
    cur.execute(f"""INSERT INTO fines (id, sum, comment) VALUES ({id}, {sum}, '{comment}')""")
    db.commit()
    user_sum = list(cur.execute(f"""SELECT SUM(sum) FROM fines where id = {id}"""))[0][0]
    cur.execute(f"""UPDATE users SET balance = {user_sum} WHERE id = {id}""")
    db.commit()
    db.close()


def check_fines(id):  # Выводит все изменения баланса пользователя, взятого по id в виде: (id, 'комментарий')
    db = sqlite3.connect("db/db.db")
    cur = db.cursor()
    info = list(cur.execute(f"""SELECT sum, comment FROM fines WHERE id = {id}"""))
    db.close()
    return info


def change_achivements(squad, num):  # Изменяет количество побед отряда номер squad на мероприятиях на num
    db = sqlite3.connect("db/db.db")
    cur = db.cursor()
    achivements = list(cur.execute(f"""SELECT achivements FROM squads WHERE number = {squad}"""))[0][0]
    cur.execute(f"""UPDATE squads SET achivements = {achivements + num} WHERE number = {squad}""")
    db.commit()
    db.close()


def set_passwords(l=8):  # Всем пользователям, не имеющим пароля сгенерирует случайным образом пароль длиной в l символов (по умолчанию 8)
    def password_generator(length):
        import random
        password = "".join(
            random.choice('ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghijklmnpqrstuvwxyz123456789') for i in range(length))
        return password
    db = sqlite3.connect("db/db.db")
    cur = db.cursor()
    users_id = list(elem[0] for elem in list(cur.execute(f"""SELECT id FROM users WHERE password IS NULL""")))
    for id in users_id:
        cur.execute(f"""UPDATE users SET password = '{password_generator(l)}' WHERE id = {id}""")
    db.commit()
    db.close()

# ----Следующие-функции-имеют-консольный-интерфейс-и-созданы-для-db_console_helper.py---- #
def add_user():
    db = sqlite3.connect("db/db.db")
    cur = db.cursor()
    firstname = input('Фамилия: ')
    name = input('Имя: ')
    lastname = input('Отчество: ')
    squad = int(input('Отряд: '))
    post = input('Должность: ')
    cur.execute(f"""INSERT INTO users (firstname, name, lastname, squad, post) VALUES ('{firstname}', '{name}', '{lastname}', {squad}, '{post}')""")
    db.commit()
    db.close()

def edit_user(id):
    db = sqlite3.connect("db/db.db")
    cur = db.cursor()
    info = list(cur.execute(f"""SELECT firstname, name, lastname, password, squad, post FROM users WHERE id={id}"""))[0]
    print('============')
    for i in info:
        print(i)
    print('============')
    firstname = input('Фамилия: ')
    name = input('Имя: ')
    lastname = input('Отчество: ')
    password = input('Пароль: ')
    squad = int(input('Отряд: '))
    post = input('Должность: ')
    cur.execute(f"""UPDATE users SET firstname='{firstname}', name='{name}', lastname='{lastname}', squad={squad}, post='{post}', password='{password}' WHERE id={id}""")
    db.commit()
    db.close()
# --------------------------------------------------------------------------------------- #
