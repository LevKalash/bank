import database  # Подключаем свой скрипт с функциями взаимодействия с базами данных


def info(hello=False):  # Выводит справку о списке команд этой консольной программы
    if hello:
        print("""
    Вас приветствует программа 
    для быстрого взаимодействия с паролями в базе данных
    ----------------------------------------------------""")
    print("""
    print_users - Выведет всех пользователей из базы данных
    print_users empty - Выведет всех пользователей из базы данных, у которых нет пароля (Null)
    
    set_passwords - Заполнит все поля без паролей (Null) случайно сгенерированными паролями длиной в 8 символов
    set_passwords n - Заполнит все поля без паролей (Null) случайно сгенерированными паролями длиной в n символов
    edit_user n - Позволяет изменить всю информацию о пользователе с id = n
    
    exit - выход из программы
    help - выведет список команд
    """)


def password_print(only_empty=False):  # Функция выводит пароли всех пользователей из базы данных
    data = database.login()
    for i in data.keys():
        if only_empty:
            if data[i][-1] == None:
                print(str(data[i][0])+': ', i+': '+data[i][-1])
        else:
            print(str(data[i][0])+': ', i+': '+data[i][-1])


info(True)
while True:
    request = input(">>")  # Ждём ввода в бесконечном цикле
    # Обработка вводов
    if request == 'exit':
        break
    elif request == 'help':
        info()
    elif 'print_users' in request and request.split()[0] == 'print_users':
        if len(request.split()) == 1:
            password_print()
        else:
            password_print(True)
    elif 'set_passwords' in request and request.split()[0] == 'set_passwords':
        if len(request.split()) == 1:
            database.set_passwords()
        else:
            database.set_passwords(int(request.split()[-1]))
    elif 'edit_user' in request:
        print(request.split()[-1])
        database.edit_user(int(request.split()[-1]))
    else:
        print('Неизвестный запрос.')