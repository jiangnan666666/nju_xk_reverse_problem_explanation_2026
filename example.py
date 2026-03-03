#自行把***补全
#除了loginPwd为密码外，其余均为学号
#loginPwd参考getpwd.js
import requests
import base64
from recognize import getchar
import json
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def encrypt(data, avy="wHm1xj3afURghi0c"):
    data = json.dumps(data)
    timestamp = int(time.time() * 1000)
    plain_text = f"{data}?timestrap={timestamp}"
    key = avy.encode("utf-8")
    aes = AES.new(key, AES.MODE_ECB)
    padded_data = pad(plain_text.encode("utf-8"), AES.block_size)
    cipher_bytes = aes.encrypt(padded_data)
    return base64.b64encode(cipher_bytes).decode("utf-8")
while True:
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',}
    while True:
        response = session.post('https://xk.nju.edu.cn/xsxkapp/sys/xsxkapp/student/4/vcode.do',headers=headers)
        data = response.json()['data']
        vode = data['vode']
        uuid = data['uuid']
        response.close()
        img = base64.b64decode(vode[22:])
        with open("captcha.jpg","wb") as f: f.write(img)
        chars = getchar()
        if chars: break
    temp = []
    for c in chars:
        (a, b) = c
        temp.append(str(a)+'-'+str(b))
    verifyCode = ','.join(temp)
    print(verifyCode)
    data = {
        'loginName': '***',
        'loginPwd': '***',
        'verifyCode': verifyCode,
        'vtoken': 'null',
        'uuid': uuid,
    }
    response = session.post('https://xk.nju.edu.cn/xsxkapp/sys/xsxkapp/student/check/login.do',headers=headers,data=data)
    print(response.json())
    token = response.json()['data']['token']
    response.close()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'token': token,
    }
    response = session.post('https://xk.nju.edu.cn/xsxkapp/sys/xsxkapp/student/***.do', headers=headers)
    electiveBatchCode = response.json()['data']['electiveBatchList'][0]['code']
    response.close()
    while True:
        try:
            data = {
                'querySetting': '{"data":{"studentCode":"***","electiveBatchCode":"'+electiveBatchCode+'","teachingClassType":"TY","checkConflict":"2","checkCapacity":"2","queryContent":""},"pageSize":"10","pageNumber":"0","order":"isChoose -"}',
            }
            response = session.post('https://xk.nju.edu.cn/xsxkapp/sys/xsxkapp/elective/publicCourse.do',headers=headers,data=data,)
            class_ = response.json()['dataList'][60]
            print("=" * 40)
            print("课程名称：", class_.get("courseName") or "无")
            print("老师：", class_.get("teacherName") or "无")
            print("校区：", class_.get("campusName") or "无", end=' ')
            print("学院：", class_.get("departmentName") or "无")
            print("上课时间地点：", class_.get("teachingPlace") or "无")
            print("学分：", class_.get("credit") or "无")
            selected = class_.get("numberOfSelected") or 0
            capacity = class_.get("classCapacity") or 0
            remaining = int(capacity) - int(selected) if str(capacity).isdigit() and str(selected).isdigit() else "未知"
            print(f"人数：已选 {selected} 人，容量 {capacity} 人，剩余 {remaining} 人")
            print("备注要求：", class_.get("extInfoXz") or "无")


            print("=" * 40)
            response.close()
            teachingClassId = class_['limitKindList'][0]['teachingClassID']
            courseKind = class_['courseKind']
            a = {"data":{"operationType":"1","studentCode":"***","electiveBatchCode":electiveBatchCode,"teachingClassId":teachingClassId,"courseKind":courseKind,"teachingClassType":"TY"}}
            addParam = encrypt(a)
            data = {
                'addParam': addParam,
                'studentCode': '***',
            }

            response = session.post('https://xk.nju.edu.cn/xsxkapp/sys/xsxkapp/elective/volunteer.do',headers=headers,data=data)
            print(response.json())
            response.close()
            time.sleep(1)
            data = {
                'querySetting': '{"data":{"studentCode":"***","electiveBatchCode":"'+electiveBatchCode+'","teachingClassType":"GG02","checkConflict":"2","checkCapacity":"2","queryContent":""},"pageSize":"10","pageNumber":"0","order":"isChoose -"}',
            }
            response = session.post('https://xk.nju.edu.cn/xsxkapp/sys/xsxkapp/elective/publicCourse.do',headers=headers,data=data,)
            class_ = response.json()['dataList'][56]
            response.close()
            print("=" * 40)
            print("课程名称：", class_.get("courseName") or "无")
            print("老师：", class_.get("teacherName") or "无")
            print("校区：", class_.get("campusName") or "无", end=' ')
            print("学院：", class_.get("departmentName") or "无")
            print("上课时间地点：", class_.get("teachingPlace") or "无")
            print("学分：", class_.get("credit") or "无")
            selected = class_.get("numberOfSelected") or 0
            capacity = class_.get("classCapacity") or 0
            remaining = int(capacity) - int(selected) if str(capacity).isdigit() and str(selected).isdigit() else "未知"
            print(f"人数：已选 {selected} 人，容量 {capacity} 人，剩余 {remaining} 人")
            print("备注要求：", class_.get("extInfoXz") or "无")
            print("=" * 40)
            response.close()
            teachingClassId = class_['teachingTimeList'][0]['teachingClassID']
            courseKind = class_['courseKind']
            a = {"data":{"operationType":"1","studentCode":"***","electiveBatchCode":electiveBatchCode,"teachingClassId":teachingClassId,"courseKind":courseKind,"teachingClassType":"TY"}}
            addParam = encrypt(a)
            data = {
                'addParam': addParam,
                'studentCode': '***',
            }
            response = session.post('https://xk.nju.edu.cn/xsxkapp/sys/xsxkapp/elective/volunteer.do',headers=headers,data=data)
            print(response.json())
            response.close()
            time.sleep(1)
        except:
            print("error")
            break
