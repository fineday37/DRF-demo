# import pytesseract
# from PIL import Image
#
# file = r'E:\option\1668412738012.png'
# image = Image.open(file)
# print(pytesseract.image_to_string(image))
import datetime
import random
import time
from threading import Thread, Lock

import pymysql
import requests


class DB:
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                port=3306,
                host="10.168.20.124",
                user="bmp",
                password="sjky2022",
                db="bmp-test",
                charset='utf8mb4'
            )
            self.cursor = self.conn.cursor()
        except pymysql.OperationalError as e:
            print("mysql error %d: %s" % (e.args[0], e.args[1]))

    def Query_Fetchone(self, sql_name):
        sql_tag = self.cursor.execute(sql_name)
        if sql_tag:
            result = self.cursor.fetchone()
            return result

    def Query_Fetchmany(self, sql_name, number):
        sql_tag = self.cursor.execute(sql_name)
        if sql_tag:
            result = self.cursor.fetchmany(number)
            return result

    def Query_Fetchall(self, sql_name):
        sql_tag = self.cursor.execute(sql_name)
        if sql_tag:
            results = self.cursor.fetchall()
            return results

    def insert(self, table_name, table_data):
        for key in table_data:
            table_data[key] = "'" + str(table_data[key] + "'")
        key = ",".join(table_data.keys())
        value = ",".join(table_data.values())
        real_sql = "insert into " + table_name + "(" + key + ") values (" + value + ")"
        self.cursor.execute(real_sql)
        self.conn.commit()

    def clear(self, table_name):
        real_sql = "delete from" + table_name + ";"
        self.cursor.execute(real_sql)
        self.conn.commit()


# 获取用户
def getList():
    res = requests.get(url="http://10.1.20.74:8080/member/getYesterdayNotifyMemberList?shopName=益好旗舰店")
    return res.json()["data"]


def BreakList(n, names):
    name = [names[i:i + n] for i in range(0, len(names), n)]
    return name


# 新增店铺
def insert_shop(shop_id, name, shop_time):
    shop = {
        'id': shop_id,
        'name': name,
        'valid': '1',
        'create_time': shop_time
    }
    DB().insert("sys_shop", shop)


# 新增客服
def insert_custcare(custcare_id, custcare_name, shop_id, create_time):
    custcare = {
        'id': custcare_id,
        'custcare_ww': custcare_name,
        'shop_id': shop_id,
        'valid': '1',
        'create_time': create_time
    }
    DB().insert("sys_custcare", custcare)


mutex = Lock()


# 新增用户
def insert_member(data, custcare_id, shop_id, create_time):
    for name in data:
        # 用户
        mbr_member = {
            'id': name,
            'member_name': name,
            'member_no': '1589506570574793379',
            'status': 'VALID',
            'create_by': 'RPA',
            'order_status': 'NOORDER',
            'member_source': 'TAOBAO',
            'wangwang': name
        }
        DB().insert("mbr_member", mbr_member)
        # 用户关联店铺客服
        mbr_member_r_custcase = {
            'member_id': name,
            'custcare_id': custcare_id,
            'shop_id': shop_id
        }
        time.sleep(0.2)
        DB().insert("mbr_member_r_custcase", mbr_member_r_custcase)
        # order_number = lambda: int(round(time.time() * 1000 * 1000))
        num = random.randint(1, 99999999999)
        mbr_member_r_label = {
            'label_id': '2000',
            'id': str(num),
            'label_group_id': '100',
            'member_id': name,
            'source': 'MQ',
            'message': '美食',
            "create_time": create_time
        }
        time.sleep(0.2)
        DB().insert("mbr_member_r_label", mbr_member_r_label)
        print(name)


def generate():
    lists = []
    for l in range(50000):
        lists.append(str(l))
    return lists


if __name__ == '__main__':
    current_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    shop_test_id = "1585868497840627777"
    shop_name = "测试旗舰店"
    custcare_test_id = '1585838035730087999'
    custcare_ww = '益好旗舰店:测试'
    # insert_shop(shop_test_id, shop_name, current_time)
    # insert_custcare(custcare_test_id, custcare_ww, shop_test_id, current_time)
    start = time.time()
    threads = []
    member_data = BreakList(1000, generate())
    for users in member_data:
        t = Thread(target=insert_member, args=(users, custcare_test_id, shop_test_id, current_time))
        threads.append(t)
    for i in threads:
        i.start()
    for j in threads:
        j.join()
    end = time.time()
    print('新增用户消耗时间: {:.2f}'.format(end - start))
