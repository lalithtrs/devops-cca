import uuid
from django.db import connection

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def createaccount(account):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO bank_accounts 
            (type_name, rate_of_interest, year_launched) 
            VALUES (%s, %s, %s)
        """,
            [account["type_name"],
            account["rate_of_interest"],
            account["year_launched"]])

def readaccounts():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM bank_accounts")
        accounts = dictfetchall(cursor)
    return accounts

def readaccount(id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM bank_accounts 
            WHERE id = %s
            """, [id])
        account = dictfetchall(cursor)[0]
    return account

def updateaccount(account,id):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE bank_accounts 
            SET type_name = %s, 
            rate_of_interest = %s, 
            year_launched = %s 
            WHERE id = %s
            """,
            [account["type_name"],
             account["rate_of_interest"],
             account["year_launched"], id])

def deleteaccount(id):
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM bank_accounts 
            WHERE id = %s
            """, [id])

def userlogin(credentials):
    with connection.cursor() as cursor1:
        cursor1.execute("""
            SELECT * FROM users 
            WHERE login_name = %s 
            AND login_password = %s
            """,
            [credentials["login_name"],
             credentials["login_password"]])
        result = dictfetchall(cursor1)

    if len(result) != 0:
        user = result[0]
        session_id = str(uuid.uuid4())
        csrf_token = str(uuid.uuid4())
        with connection.cursor() as cursor2:
            cursor2.execute("""
                INSERT INTO sessions 
                (session_id, user_id) VALUES (%s, %s)
                """,
                [session_id, user["user_id"]])
        with connection.cursor() as cursor3:
            cursor3.execute("""
                INSERT INTO csrf_tokens 
                (token,session_id) VALUES (%s, %s)
                """,
                [csrf_token,session_id])
        return session_id
    else:
        return None
def getuserbyname(name):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_id 
            FROM users
            WHERE login_name = %s
        """,[name])
        return dictfetchall(cursor)[0]

def getuser(session_id):
    if session_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT a.user_id,a.login_name,b.role_name,f.token 
                FROM user_role c 
                INNER JOIN users a ON c.user_id = a.user_id 
                INNER JOIN roles b ON c.role_id = b.role_id
                INNER JOIN sessions d ON d.user_id = a.user_id
                INNER JOIN csrf_tokens f ON f.session_id = d.session_id 
                WHERE d.session_id = %s
                """, [session_id])
            result = dictfetchall(cursor)
        if len(result) != 0:
            return result[0]
        else:
            return {"login_name":"","role_name":"ROLE_PUBLIC","token":""}
    else:
        return {"login_name": "","role_name": "ROLE_PUBLIC","token":""}

def getuserbalance(session_id):
    if session_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT a.balance_amount 
                FROM user_accounts a 
                INNER JOIN users b ON a.user_id = b.user_id 
                INNER JOIN sessions c ON c.user_id = a.user_id
                WHERE c.session_id = %s
                """, [session_id])
            result = dictfetchall(cursor)
        if len(result) != 0:
            return result[0]
        else:
            return {"balance_amount":0}
    else:
        return {"balance_amount":0}

def deletesession(session_id):
    with connection.cursor() as cursor1:
        cursor1.execute("""
            DELETE FROM csrf_tokens 
            WHERE session_id = %s
            """, [session_id])
    with connection.cursor() as cursor2:
        cursor2.execute("""
            DELETE FROM sessions 
            WHERE session_id = %s
            """, [session_id])


def transfermoney(session_id,transfer):
    uuser = getuser(session_id)
    from_user = uuser["login_name"]
    from_user_id = uuser["user_id"]
    to_user = transfer["to_user"]
    to_user_id = getuserbyname(to_user)["user_id"]
    transfer_amount = transfer["transfer_amount"]
    print(to_user)
    with connection.cursor() as cursor1:
        cursor1.execute("""
            UPDATE user_accounts 
            SET balance_amount = balance_amount - %s 
            WHERE user_id = (
            SELECT user_id 
            FROM users 
            WHERE login_name= %s );
            """, [transfer_amount, from_user])
    with connection.cursor() as cursor2:
        cursor2.execute("""
            UPDATE user_accounts 
            SET balance_amount = balance_amount + %s 
            WHERE user_id = (
            SELECT user_id 
            FROM users 
            WHERE login_name= %s );
            """,[transfer_amount, to_user])
    with connection.cursor() as cursor3:
        cursor3.execute("""
            INSERT INTO transactions 
            (from_user, to_user, amount)
            VALUES(%s, %s, %s)
            """,
            [from_user_id,to_user_id,transfer_amount])

def addcomment(session_id,comment):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO user_comments
            (username, comment) 
            VALUES (%s, %s)
            """,
            [getuser(session_id)["login_name"],
             comment["user_comment"]])

def getcomments():
    user_comments = ""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user_comments")
        comments = dictfetchall(cursor)
    for comment in comments:
        user_comments = (user_comments +
                         "<p><b>" + comment["username"] +
                         ":</b> " + comment["comment"] +
                         "</p>")
    return user_comments


def getcsrftoken(session_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM csrf_tokens 
            WHERE session_id= %s
            """, [session_id])
        result = dictfetchall(cursor)
        if len(result) != 0:
            return result[0]
        else:
            return None

def validatecsrftoken(csrf_token,session_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM csrf_tokens 
            WHERE token = %s AND session_id= %s
            """, [csrf_token,session_id])
        result = dictfetchall(cursor)
        if len(result) != 0:
            return True
        else:
            return False