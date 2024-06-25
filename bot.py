import telebot
from telebot import types  # для указание типов
import config
import time
import datetime
import sys
import math
import schedule
import threading
import pymysql
import shifr_kuz as gh #grasshopper
import re
#import random
import bcrypt


# Создаем переменную-флаг
bot_restarted = True
auto_send = False
OldArrayKey = [4, 0, 8, 0, 2, 6, 1, 8, 2, 0, 1, 2, 1, 6, 3, 5, 0, 3, 4, 6, 8, 2, 7, 2, 0, 5, 5, 5, 7, 9, 7, 0, 9, 2,
                 2, 3, 7, 5, 0, 6, 6, 6, 1, 7, 7, 4, 4, 2, 6, 1]

ArrayKey = [4, 0, 8, 0, 2, 6, 1, 8, 2, 0, 1, 2, 1, 6, 3, 5, 0, 3, 4, 6, 8, 2, 7, 2, 0, 5, 5, 5, 7, 9, 7, 0, 9, 2,
                 2, 3, 7, 5, 0, 6, 6, 6, 1, 7, 7, 4, 4, 2, 6, 1]

DataFromDB = "Пусто"
old_encrypted_data_from_db = ""
old_key_from_DB = ""
time_of_the_message_from_db = ""
counter_for_update_graph = 0

# Словарь для хранения состояния пользователя
user_state = {}

authorized_users = []

# Константы для состояний
STATE_AUTH = "auth"
STATE_MAIN_MENU = "main_menu"

T = 0
H = 0
P = 0
R = 0
S = 0
old_data_for_graph = ""
connected_mk = 0


bot = telebot.TeleBot(config.TOKEN)
# Событие для сигнализации основному потоку о завершении планировщика
stop_event = threading.Event()

def getQuery(query):
    getted_string = "error"
    try:
        # Подключение к базе данных
        connection = pymysql.connect(host='127.0.0.1',  # Адрес сервера базы данных
                                     port=3306,
                                     user='root',  # Имя пользователя для подключения к базе данных
                                     password='root',  # Пароль для подключения к базе данных
                                     db='dipib',  # Имя базы данных
                                     charset='utf8',  # Кодировка для подключения к базе данных
                                     cursorclass=pymysql.cursors.DictCursor)  # Указание типа курсора
        print("successfully connected to get key with id=2")

        try:
            # Создание курсора
            cursor = connection.cursor()

            # Запрос для чтения данных из таблицы

            # Выполнение запроса
            cursor.execute(query)

            # Получение результата выполнения запроса
            result = cursor.fetchone()
            getted_string = result['encrypted']
            # Вывод значения на консоль
            print(getted_string)

            # Закрытие курсора и соединения
            cursor.close()
        finally:
            connection.close()
    except Exception as ex:
        print("Connection refused... (getQuery)")
        print(ex)
    return getted_string

def SendSensorData(query, word):
    try:
        # Подключение к базе данных
        connection = pymysql.connect(host='127.0.0.1',  # Адрес сервера базы данных
                                     port=3306,
                                     user='root',  # Имя пользователя для подключения к базе данных
                                     password='root',  # Пароль для подключения к базе данных
                                     db='dipib',  # Имя базы данных
                                     charset='utf8',  # Кодировка для подключения к базе данных
                                     cursorclass=pymysql.cursors.DictCursor)  # Указание типа курсора
        print("successfully connected to set key=2 with id=2")

        try:
            # Создание курсора
            cursor = connection.cursor()

            # Запрос для чтения данных из таблицы
            # query = "SELECT encrypted FROM sensor_data WHERE id = 2"


            # Выполнение запроса
            cursor.execute(query, (word,))
            connection.commit()

            # Закрытие курсора и соединения
            cursor.close()
        finally:
            connection.close()
    except Exception as ex:
        print("Connection refused...(SendSensorData) or journal")
        print(ex)

def decrytped_data(encryp_hex, OldArrayKey):
    try:
        # Создание списка для хранения разделенных значений
        values = []
        encryp_hex = encryp_hex.replace(' ', '')
        # Разделение строки по символу '0x'
        tokens = encryp_hex.split('0x')

        # Преобразование разделенных значений в числа и добавление их в список
        for token in tokens:
            if token:  # Пропускаем пустые токены
                values.append(int(token, 16))

        mas = []
        word_encryp_data = ""
        for i in range(0,len(OldArrayKey),2):
            mas.append(OldArrayKey[i] * 10 + OldArrayKey[i+1])
        for i in range(len(values)):
            word_encryp_data += chr(mas[i] ^ values[i])
        print(f"Расшифрованное значение: {word_encryp_data}")
        return word_encryp_data
    except Exception as ex:
        print("Connection refused...(decrytped_data)")
        print(ex)
    return "ошибка расшифровки данных"

def gen_key():
    data_time = datetime.datetime.now()
    print(f"Ключ: {str(data_time)}")
    x = 0
    for z in str(data_time):
        x = x * 60 + ord(z)
        # print(z, ord(z))
    # print(x)

    # 14446601786558765474824545554632744915981346148**0.5

    # y = 17
    y = x
    numbers_posle_zapyatoy = []
    if y == round(int(y ** 0.5) ** 2):
        y += 1
        print("next")
    a = int(y ** 0.5)
    b = (y - a ** 2) * 100
    # print(a, end=",")
    p0 = 0

    for i in range(200):
        # t1=time()
        x = b // (2 * a * 10)
        z = (2 * a * 10 + x) * x
        while z > b:
            x -= 1
            z = (2 * a * 10) * x
        # z= (2*a*10+x)*x
        b = (b - z) * 100
        a = a * 10 + x
        numbers_posle_zapyatoy.append(x)
        # t2=time()
        # print(i,t2-t1)

        # print(x,end="")
        # p=(math.log((t2-t1),10))
        # if abs(p-p0)>=1.4:
        #  print(i,"10^",int(p),"сек")
        #  p0=int(p)
    new_numbers_posle_zapyatoy =  numbers_posle_zapyatoy[50:100]
    print(new_numbers_posle_zapyatoy)
    return new_numbers_posle_zapyatoy

def shifhr_key(OldArrayKey, NewArrayKey):
    new_hex_hey = ""
    for i in range(len(NewArrayKey)):
        old_key_ord = ord(str(OldArrayKey[i]))
        new_key_ord = ord(str(NewArrayKey[i]))
        new_hex_hey += hex(old_key_ord ^ new_key_ord) + " "
    return new_hex_hey


def job_continue(mess):
    string_m = mess
    correct_or_not = 0
    global T
    global H
    global P
    global R
    global S
    global auto_send
    global time_of_the_message_from_db
    string_without_sum = ""

    try:
        string_m = string_m.replace(" ", "")
        string_m = string_m.replace("-1", "0")
        # Разделим строку по буквам и значениям
        pattern = "([A-Z])([0-9]+)"
        matches = re.findall(pattern, string_m)

        # Создадим словарь с переменными буквами и значениями
        data = {}
        for match in matches:
            data[match[0]] = int(match[1])

        # Получим значения переменных int
        T = data["T"]  # температура
        H = data["H"]  # влажность
        P = data["P"]  # давление
        R = data["R"]  # газовое сопротивление bme680
        S = data["S"]  # дым mq-2
        C = data["C"]  #чек сумма
        string_without_sum += "T" + str(T) + "H" + str(H) + "P" + str(P) + "GR" + str(R) + "S" + str(S)

        query = """
            INSERT INTO journal (comment)
            VALUES (%s)
        """
        print(f"kontr sum={C}" )
        c_up = "Чек сумма не сходится! Угроза изменения прошивки прибора"
        if C != 22: #27
            SendSensorData(query, c_up)
            c_up = c_up + "\n" + time_of_the_message_from_db
            for user_id in authorized_users:
                bot.send_message(user_id, text=c_up)



        # Выведем значения переменных
        """
        print("T:", T)
        print("H:", H)
        print("P:", P)
        print("R:", R)
        print("S:", S)
        """
        t_up = "ОПАСНОСТЬ! Температура выше 58 *С и равна= " + str(T) + " *C. Возможен ПОЖАР!"
        s_up = "ОПАСНОСТЬ! Концентрация дыма выше 1000 ppm и равна= " + str(S) + " ppm. Возможен ПОЖАР!"
        r_up = "ОПАСНОСТЬ! Концентрация вредных веществ в воздухе выше 500 IAQ и равна= " + str(R) \
               + " IAQ. Проветрите помещение"
        r_low = "ОПАСНОСТЬ! Концентрация вредных веществ в воздухе выше 300 IAQ и равна= " + str(R) \
               + " IAQ. Проветрите помещение"

        t_error = "Температурный датчик работает некорректно"
        s_error = "Газовый датчик работает некорректно"

        correct_or_not = 1

        if auto_send == True:
            if T > 58:
                SendSensorData(query, t_up)
                t_up = t_up + "\n" + time_of_the_message_from_db
                for user_id in authorized_users:
                    bot.send_message(user_id, text=t_up)
            if S > 1000:
                SendSensorData(query, s_up)
                s_up = s_up + "\n" + time_of_the_message_from_db
                for user_id in authorized_users:
                    bot.send_message(user_id, text=s_up)
            if R > 500:
                SendSensorData(query, r_up)
                r_up = r_up + "\n" + time_of_the_message_from_db
                for user_id in authorized_users:
                    bot.send_message(user_id, text=r_up)
            if R > 300:
                SendSensorData(query, r_low)
                r_low = r_low + "\n" + time_of_the_message_from_db
                for user_id in authorized_users:
                    bot.send_message(user_id, text=r_low)
            if T == 0:
                SendSensorData(query, t_error)
                t_error = t_error + "\n" + time_of_the_message_from_db
                for user_id in authorized_users:
                    bot.send_message(user_id, text=t_error)
            if S == -1:
                SendSensorData(query, s_error)
                s_error = s_error + "\n" + time_of_the_message_from_db
                for user_id in authorized_users:
                    bot.send_message(user_id, text=s_error)

    except Exception as ex:
        print("Расшифрованное слово не соответсвует норме")
        print(ex)
        correct_or_not = 2
    print(f'correct_or_not = {correct_or_not}')
    if(correct_or_not == 1):
        ###TO DB-------------------------------------------
        if (len(string_without_sum) < 32):
            string_without_sum += (32 - len(string_without_sum)) * " "
        # str = str.replace(" ", "")
        password = "evo_kak"  # Ввод пароля

        # Получение ключей для шифрования и расшифрования
        K = gh.getKeys(password)

        # Шифрование
        textEncrypt = gh.encrypt(string_without_sum, K)
        query = """
            INSERT INTO data_all_en (dan)
            VALUES (%s)
        """
        SendSensorData(query, textEncrypt)
        # Расшифрование
        # textDecrypt = gh.decrypt(textEncrypt, K)
        ###END------------------------------------------------------
        DataPlusTime = string_without_sum + str(datetime.datetime.now())
        with open("C:/Users/YodaB/IdeaProjects/IB_diplom/src/OneData.txt", "w") as f:
            f.write(DataPlusTime)
            f.truncate()  # Очищает файл, оставляя только одну строку

def get_first_row_and_delete(cursor):
    cursor.execute("SELECT * FROM data_for_graph ORDER BY id LIMIT 1")
    row = cursor.fetchone()
    if row:
        id_to_delete = row['id']  # предполагая, что id находится в ключе 'id'
        cursor.execute("DELETE FROM data_for_graph WHERE id = %s", (id_to_delete,))
        return True
    return False

def insert_new_row(cursor, T, H, P, S, R):
    try:
        # Вставка новой строки
        cursor.execute(
            "INSERT INTO data_for_graph (temp, hum, press, smoke, pollution) VALUES (%s, %s, %s, %s, %s)",
            (T, H, P, S, R)
        )
        print("Добавлена новая строка в базу graf")
    except Exception as e:
        print(f"Ошибка при вставке новой строки: {e} в базу graf")

def update_graph():
    global T
    global H
    global P
    global R
    global S
    global old_data_for_graph
    new_data_for_graph = str(T+H+P+R+S)
    if old_data_for_graph != new_data_for_graph:
        # Подключение к базе данных
        connection = pymysql.connect(host='127.0.0.1',  # Адрес сервера базы данных
                                     port=3306,
                                     user='root',  # Имя пользователя для подключения к базе данных
                                     password='root',  # Пароль для подключения к базе данных
                                     db='dipib',  # Имя базы данных
                                     charset='utf8',  # Кодировка для подключения к базе данных
                                     cursorclass=pymysql.cursors.DictCursor)  # Указание типа курсора
        print("successfully connected to get key with base graph")
        if T != 0 and H != 0 and P != 0:
            try:
                cursor = connection.cursor()
                if get_first_row_and_delete(cursor):
                    insert_new_row(cursor, T, H, P, S, R)
                    connection.commit()
                    print("Старая строка удалена и новая добавлена")
                else:
                    print("Нет строк для удаления")
            except Exception as e:
                print(f"Ошибка: {e}")
            finally:
                cursor.close()
                connection.close()
        old_data_for_graph = new_data_for_graph

def getPas(query):
    """
    Запрос к базе данных для получения пароля по логину.

    Args:
        query: Строка запроса к базе данных.

    Returns:
        Строка с паролем, если запрос был успешным,
        иначе "error".
    """
    getted_string = "error"
    try:
        # Подключение к базе данных
        connection = pymysql.connect(host='127.0.0.1',
                                     port=3306,
                                     user='root',
                                     password='root',
                                     db='dipib',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            # Создание курсора
            cursor = connection.cursor()

            # Выполнение запроса
            cursor.execute(query)

            # Получение результата выполнения запроса
            result = cursor.fetchone()
            if result:
                getted_string = result['password']
                print(getted_string)
            else:
                print("Запрос не вернул результатов. Такого пользователя нет")

            # Закрытие курсора и соединения
            cursor.close()
        finally:
            connection.close()
    except Exception as ex:
        print("Connection refused... (getQuery)")
        print(ex)
    return getted_string

# Функции для проверки ввода
def clean_input(user_input):
    # Убираем пробелы и очищаем ввод от нежелательных символов
    cleaned_input = re.sub(r'\s+', '', user_input)  # Убираем пробелы
    return cleaned_input

def is_valid_login_password(user_input):
    cleaned_input = clean_input(user_input)
    # Проверяем, соответствует ли формат "логин/пароль" без пробелов и лишних символов
    return re.match(r"^[A-Za-zА-Яа-яЁё0-9]+/[A-Za-zА-Яа-яЁё0-9]+$", cleaned_input) is not None

def is_valid_single_word(user_input):
    cleaned_input = clean_input(user_input)
    # Проверяем, что ввод состоит только из букв и цифр
    return re.match(r"^[A-Za-zА-Яа-яЁё0-9]+$", cleaned_input) is not None

# Допустимые команды с пробелами
allowed_commands_with_spaces = ["Как меня зовут?", "Что я могу?", "Вернуться в главное меню", "Получить данные",
                                "Вкл/выкл авто-отправку", "👋 Поздороваться", "❓ Задать вопрос"]

def is_allowed_command_with_spaces(user_input):
    return user_input in allowed_commands_with_spaces


def job():
    print("I'm working...")
    global old_encrypted_data_from_db
    global old_key_from_DB
    encrypted_data_from_db = ""
    queryGet = "SELECT encrypted FROM sensor_data WHERE id = 2"
    response_from_get_key = getQuery(queryGet)
    global bot_restarted
    global OldArrayKey
    global ArrayKey
    global DataFromDB
    global connected_mk
    global time_of_the_message_from_db
    global counter_for_update_graph

    counter_for_update_graph +=1

    # Проверяем, был ли бот перезагружен
    if bot_restarted:
        # Отправляем приветственное сообщение
        if response_from_get_key != "1":
            query1 = "UPDATE sensor_data SET encrypted = 2 WHERE id = %s"
            SendSensorData(query1, "2")
        # Сбрасываем флаг
        bot_restarted = False
    if response_from_get_key == "22" or response_from_get_key == "1":
        queryGetData = "SELECT encrypted FROM sensor_data WHERE id = 1"
        encrypted_data_from_db = getQuery(queryGetData)
        DataFromDB = decrytped_data(encrypted_data_from_db, OldArrayKey)
        ArrayKey = OldArrayKey
        NewArrayKey = gen_key()
        word_ecnrypted_new_key = shifhr_key(OldArrayKey, NewArrayKey)
        query_for_update = "UPDATE sensor_data SET encrypted = %s WHERE id = 2"
        SendSensorData(query_for_update, word_ecnrypted_new_key)
        ArrayKey = NewArrayKey
        old_encrypted_data_from_db = encrypted_data_from_db
        job_continue(DataFromDB)
        old_key_from_DB = queryGet

    if response_from_get_key == "yes":
        queryGetData = "SELECT encrypted FROM sensor_data WHERE id = 1"
        encrypted_data_from_db = getQuery(queryGetData)
        print(f"Old_enc_data = {old_encrypted_data_from_db}")
        print(f"New_enc_data = {encrypted_data_from_db}")

        if(old_encrypted_data_from_db != encrypted_data_from_db):
            connected_mk = 0
            DataFromDB = decrytped_data(encrypted_data_from_db,
                                        ArrayKey)  # РАСШИФРОВАННЫЕ ДАННЫЕ!!!!!!!!!!!!!!!!!!!!!!!
            NewArrayKey = gen_key()
            word_ecnrypted_new_key = shifhr_key(ArrayKey, NewArrayKey)
            query_for_update = "UPDATE sensor_data SET encrypted = %s WHERE id = 2"
            SendSensorData(query_for_update, word_ecnrypted_new_key)
            ArrayKey = NewArrayKey
            old_encrypted_data_from_db = encrypted_data_from_db
            #DataPlusTime = DataFromDB + str(datetime.datetime.now())
            time_of_the_message_from_db = str(datetime.datetime.now())
            job_continue(DataFromDB)
            old_key_from_DB = queryGet
    if old_key_from_DB == queryGet:
        connected_mk += 1
    if connected_mk == 5:
        query = """
            INSERT INTO journal (comment)
            VALUES (%s)
        """
        SendSensorData(query, "Потеряно соединение с прибором")
        for user_id in authorized_users:
            bot.send_message(user_id, text="Потеряно соединение с прибором")
    if counter_for_update_graph == 10:
        counter_for_update_graph = 0
        update_graph()



# Запускаем планировщик в отдельном потоке
def schedule_thread():
    while not stop_event.is_set():  # Продолжаем работать, пока не получим сигнал о завершении
        schedule.run_pending()
        time.sleep(1)

# Создаем отдельный поток для планировщика и запускаем его
schedule_thread = threading.Thread(target=schedule_thread)
schedule_thread.start()


@bot.message_handler(commands=['start', 'help'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("Авторизоваться")
    markup.add(btn)
    bot.send_message(message.chat.id, "Добро пожаловать! Нажмите кнопку для авторизации.", reply_markup=markup)
    user_state[message.chat.id] = STATE_AUTH

# Обработка нажатия на кнопку "Авторизоваться"
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == STATE_AUTH)
def authorize(message):
    if not is_valid_single_word(message.text):
        bot.send_message(message.chat.id, "Неверный формат. Пожалуйста, введите одно слово или нажмите на кнопку")
        return
    if message.text == "Авторизоваться":
        bot.send_message(message.chat.id, "Введите ваш логин и пароль, пример: user/password")
        bot.register_next_step_handler(message, check_password)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, нажмите 'Авторизоваться' для продолжения.")

# Проверка пароля
def check_password(message):
    user_input = str(message.text)
    if not is_valid_login_password(user_input):
        bot.send_message(message.chat.id, "Неверный формат. Пожалуйста, введите ваш логин и пароль в формате: user/password")
        start(message)
        return
    pas_log = message.text
    parts = pas_log.split("/")
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Неверный формат. Пожалуйста, введите ваш логин и пароль в формате: user/password")
        start(message)
        return

    username = str(parts[0])
    password = str(parts[1])
    query = f"SELECT password FROM usr WHERE username = '{username}'"
    password_from_db = getPas(query)

    if not password_from_db or password_from_db == "error":
        bot.send_message(message.chat.id, "Ошибка получения данных от БД или пользователь не найден")
        start(message)
        return

    try:
        password_from_db = password_from_db.encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), password_from_db):
            bot.send_message(message.chat.id, "Авторизация успешна! Добро пожаловать в главное меню.")
            user_state[message.chat.id] = STATE_MAIN_MENU
            authorized_users.append(message.chat.id)  # Добавляем пользователя в список авторизованных
            show_main_menu(message)
        else:
            bot.send_message(message.chat.id, "Неверный пароль. Пожалуйста, попробуйте снова.")
            start(message)
    except Exception as ex:
        print("Error word password")
        bot.send_message(message.chat.id, "Некорректный ввод")
        print(ex)

# Показ главного меню
def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    btn2 = types.KeyboardButton("❓ Задать вопрос")
    btn3 = types.KeyboardButton("Получить данные")
    btn4 = types.KeyboardButton("Вкл/выкл авто-отправку")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id,
                     text="Привет, я отправщик данных с датчика!"
                     .format(message.from_user), reply_markup=markup)

#@bot.message_handler(content_types=['text'])
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == STATE_MAIN_MENU)
def func(message):
    global auto_send
    global time_of_the_message_from_db
    user_input = message.text
    # Проверка на допустимые команды с пробелами
    if not is_allowed_command_with_spaces(user_input):
        if not is_valid_single_word(user_input):
            bot.send_message(message.chat.id, "Неверный формат. Пожалуйста, введите одно слово или нажмите на кнопку")
            return
    if (message.text == "👋 Поздороваться"):
        bot.send_message(message.chat.id, text="Привеет, я рад что вы решили получить данные с датчика")
    elif (message.text == "Получить данные"):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        #bot.send_message(message.chat.id, text="Пару мгновений")
        try:
            string = DataFromDB.replace(" ", "")
            string = string.replace("-1", "0")

            # Разделим строку по буквам и значениям
            pattern = "([A-Z])([0-9]+)"
            matches = re.findall(pattern, string)

            # Создадим словарь с переменными буквами и значениями
            data = {}
            for match in matches:
                data[match[0]] = int(match[1])


            # Получим значения переменных int
            T = data["T"]  # температура
            H = data["H"]  # влажность
            P = data["P"]  # давление
            R = data["R"]  # газовое сопротивление bme680
            S = data["S"]  # дым mq-2

            string_for_user = "Температура = " + str(T) + " *C" + " Влажность = " + str(H) + " % " + \
            "Атмосферное давление = " + str(P) + " мм.рт.ст. Качество воздуха = " + str(R) + " IAQ " + \
                " Дымовое загрязнение = " + str(S) + " ppm \n"
            # Выведем значения переменных
            """
            print("T:", T)
            print("H:", H)
            print("P:", P)
            print("R:", R)
            print("S:", S)
            """
            t_up = "ОПАСНОСТЬ! Температура выше 58 *С и равна= " + str(T) + " *C. Возможен ПОЖАР!"
            s_up = "ОПАСНОСТЬ! Концентрация дыма выше 1000 ppm и равна= " + str(S) + " ppm. Возможен ПОЖАР!"
            r_up = "ОПАСНОСТЬ! Концентрация вредных веществ в воздухе выше 151 IAQ и равна= " + str(R) \
                   + " IAQ. Проветрите помещение"

            if T > 58:
                string_for_user += t_up
            if S > 1000:
                string_for_user += s_up
            if R > 151:
                string_for_user += r_up
            string_for_user += "\n" + time_of_the_message_from_db
            bot.send_message(message.chat.id, text=string_for_user)

        except Exception as ex:
            print("Расшифрованное слово не соответсвует норме")
            print(ex)
            string_for_user = "Сбой обработки сообщения. Проверьте wifi-соединение прибора"
            bot.send_message(message.chat.id, text=string_for_user)



    elif (message.text == "Вкл/выкл авто-отправку"):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        if not auto_send:
            bot.send_message(message.chat.id, text="Авто-отправка включена")
            auto_send = True
        else:
            bot.send_message(message.chat.id, text="Авто-отправка выключена")
            auto_send = False

    elif (message.text == "❓ Задать вопрос"):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        btn1 = types.KeyboardButton("Как меня зовут?")
        btn2 = types.KeyboardButton("Что я могу?")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, back)
        bot.send_message(message.chat.id, text="Задай мне вопрос", reply_markup=markup)

    elif (message.text == "Как меня зовут?"):
        bot.send_message(message.chat.id, "Я CleAir - бот доставщик данных ")

    elif message.text == "Что я могу?":
        bot.send_message(message.chat.id, text="Я могу доставлять Вам данные")

    elif (message.text == "Вернуться в главное меню"):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button1 = types.KeyboardButton("👋 Поздороваться")
        button2 = types.KeyboardButton("❓ Задать вопрос")
        button3 = types.KeyboardButton("Получить данные")
        button4 = types.KeyboardButton("Вкл/выкл авто-отправку")
        markup.add(button1, button2, button3, button4)
        bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммировал..")


# Добавляем задание в планировщик
schedule.every(30).seconds.do(job)


bot.polling(none_stop=True)