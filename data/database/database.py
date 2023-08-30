import sqlite3
conn = sqlite3.connect('db.db')
cursor = conn.cursor()

async def getAllRequests():
    """
    Возвращает все реквесты в виде массива картежей
    :return:
    """
    data = cursor.execute("SELECT * FROM requests").fetchall()
    if data:
        return data
    else:
        return None

async def updateTime(id, newtime):
    """
    Обновляет cooldown
    :param id:
    :param newtime:
    :return:
    """
    cursor.execute("UPDATE requests SET cooldown = ? WHERE id = ?", (newtime, id))
    conn.commit()

