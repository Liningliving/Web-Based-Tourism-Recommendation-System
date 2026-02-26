from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2
import requests
import jieba

app = Flask(__name__)
CORS(app, supports_credentials=True)

# 连接数据库
server = "127.0.0.1"  # 连接服务器地址
user = "postgres"  # 连接帐号
password = "welcome"  # 连接密码
port = "5432"
database = "tourism_recommendation"

def listToString(s):
    # initialize an empty string
    str1 = ""
    # traverse in the string
    for ele in s:
        str1 += ele
    # return string
    return str1

@app.route("/")
def welcome():
    return "Hello World!:)"

@app.route("/login", methods=['GET', 'POST'])
def login():
    pwd = request.args.get("pwd")
    name = request.args.get("name")
    #print(pwd,name)
    #search data in the customer table
    conn = psycopg2.connect(database=database, user=user, password=password, host=server, port=port)  # 获取连接
    cursor = conn.cursor()
    search_user = "SELECT user_name,password FROM users WHERE user_name='{}'".format(name)
    cursor.execute(search_user)
    conn.commit()
    # fetch

    row = cursor.fetchone()
    if isinstance(row, tuple):
        res = {'name':row[0],'pwd':row[1] }
        # print("dfafdsafewg")
    else:
        res = {'name':"None",'pwd':"None" }
        # print("Dfafwe")
    cursor.close()
    conn.close()
    return jsonify(res)

@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    pwd = request.args.get("pwd")
    name = request.args.get("name")
    adult = request.args.get("adult")
        #search data in the customer table to see if the user is a known user.
    conn = psycopg2.connect(database=database, user=user, password=password, host=server, port=port)  # 获取连接
    cursor = conn.cursor()
    search_user = "SELECT count(*) as num FROM users WHERE user_name='{}'".format(name)
    cursor.execute(search_user)
    conn.commit()
    # fetch
    row = cursor.fetchone()
    # res = {"num": row[0]}
    cursor.close()
    # Check if the username is unique.
    if row[0] == 0:
        # This username is unique, so we can save it to our database.
        cursor = conn.cursor()
        ustr = "insert into users(user_name, password,adult) values('{}','{}','{}')".format(name, pwd,adult)
        cursor.execute(ustr)
        res = {"msg": "success"}
    else:
        res = {"msg": "error"}
    conn.commit()
    cursor.close()
    return jsonify(res)

@app.route("/search_nearby", methods=['GET', 'POST']) # POST GET
def age_limit_and_save_preference():
    # 获取参数
    preference = request.args.get("preference")
    name = request.args.get("name")

    #save preference
    conn = psycopg2.connect(database = database, user = user, password = password, host = server,port = port)  #获取连接
    cursor_fetch = conn.cursor()

    sql_fetch = "SELECT preference FROM users WHERE user_name='{}'".format(name)
    cursor_fetch.execute(sql_fetch)
    # fetch
    the_user_preference = cursor_fetch.fetchone()
    # res = {"adult":row[0]}
    cursor_update = conn.cursor()
    if the_user_preference[0] != None:
        sql_update = "update users set preference = concat('{}','{}') WHERE user_name='{}'".format(preference,
                                                                                             the_user_preference[0],
                                                                                               name)
    else:
        preference =  ";" + preference
        sql_update = "update users set preference = concat('{}') WHERE user_name='{}'".format(preference,
                                                                                                   name)
    cursor_fetch.execute(sql_update)
    cursor_update.close()
    cursor_fetch.close()

    #detect if the user is an adult.
    cursor = conn.cursor()
    sql = "SELECT adult FROM users WHERE user_name='{}'".format(name)
    # sql = "SELECT adult FROM users WHERE user_name='Attie Lin'"
    cursor.execute(sql)
    conn.commit()
    #fetch
    row = cursor.fetchone()
    res = {"adult":row[0]}
    cursor.close()
    conn.close()

    return jsonify(res)

@app.route("/edit_preference", methods=['GET', 'POST'])
def edit_preference():
    with open('stop_words.txt', encoding='utf-8') as f:  # 可根据需要打开停用词库，然后加上不想显示的词语
        con = f.readlines()
        stop_words = set()  # 集合可以去重
        for i in con:
            i = i.replace("\n", "")  # 去掉读取每一行数据的\n
            stop_words.add(i)

    name = request.args.get("name")
    # fetch the user's preference data.
    conn = psycopg2.connect(database=database, user=user, password=password, host=server, port=port)  # 获取连接
    cursor = conn.cursor()
    cursor_update = conn.cursor()
    search_user = "SELECT preference FROM users WHERE user_name='{}'".format(name)
    # search_user = "SELECT preference FROM users WHERE user_name='Attie Lin'"
    cursor.execute(search_user)
    conn.commit()
    # fetch
    row = cursor.fetchone()
    # res = {"num": row[0]}
    preference = row[0]

    result = []
    for word in jieba.lcut(preference):
        if word not in stop_words:
            result.append(word)
    result = listToString(result)

    #upate the result into the user's preference column.
    sql_update = "update users set preference ='{}' WHERE user_name='{}'".format(result, name)
    # sql_update = "UPDATE users SET preference ='{}' WHERE user_name='Attie Lin'".format(result)
    cursor_update.execute(sql_update)
    conn.commit()
    print(result)
    cursor.close()
    cursor_update.close()
    conn.close()

    res = {"result": "success"}
    return jsonify(res)

if __name__ == "__main__":
    app.debug = True # 设置调试模式，生产模式的时候要关掉debug
    app.run(host='127.0.0.1', port=5000)
