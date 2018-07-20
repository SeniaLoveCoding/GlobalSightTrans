# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 20:54:16 2018

@author: YUEShengya

注意：运行此程序前请 pip install beautifulsoup4
"""
from bs4 import BeautifulSoup
import re
import http.client 
import hashlib  
import json 
import urllib
import random

# 百度翻译
def baidu_translate(content):   
    appid = '20170601000049700' # 百度翻译id
    secretKey = 'OHqQEmHWI6bQ7iYSAip6' # 百度翻译key
    
    httpClient = None  
    myurl = '/api/trans/vip/translate' 
    q = content	# 待译内容
    	
    salt = random.randint(32768,65536)  # 随机数salt
    sign = appid + q + str(salt) + secretKey  
    sign = hashlib.md5(sign.encode()).hexdigest() 
    fromLang = 'en'# 源语言
    toLang = 'zh'# 目标语言
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign  # 拼接url     
    try:         
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')  
        httpClient.request('GET', myurl)  # 请求HTTP响应
        response = httpClient.getresponse()  
        jsonResponse = response.read().decode("utf-8")  # 获得json格式结果
        js = json.loads(jsonResponse)# json格式的结果转换为字典结构  
        dst = str(js["trans_result"][0]["dst"]) # 翻译后的结果文本dst  
        return (dst);
    except Exception as e:# 异常处理
       print (e)
    finally:
        if httpClient:
           httpClient.close() 

# 处理并拼接带标签的字符串     
def getTranSentence(s):
    list_h=[] # 用于存储html
    list_t=[] # 用于存储文本
    for i in re.finditer('<.*?>',s): # 获取所有标签
        list_h.append(i)  
    soup = BeautifulSoup(s,'lxml') # BeautifulSoup为一个HTML解析库
    for i in soup.strings:  # 获取所有需要翻译的文本
        list_t.append(i)
    list_new=[]
    for i in list_t:
        t=baidu_translate(i)
        list_new.append(t)
    # 查看先遍历哪个
    out=''
    if(len(list_new)>len(list_h)):
       for i,v in enumerate(list_new):
           try:
               out+=v
               out+=list_h[i].group()
           except:
                pass              
    else:
        for i,v in enumerate(list_h):
            try:
                out+=v.group()
                out+=list_new[i]
            except:
               pass
    return out

# 主函数：遍历原文件->找出需要翻译的字符串部分->翻译并拼接结果->按序存入译后文件      
def main():
    with open('LocaleResource_en_US.properties', 'r') as input_file:
        # 汉化后的输出文件为LocaleResource_zh_CN.properties
        with open('LocaleResource_zh_CN.properties', 'w') as output_file:
            # 遍历英文原文
            for line in input_file.readlines():
                # 1.对于不用翻译的行
                if not line.strip():
                    # 直接写入输出文件
                    print(line)
                    output_file.write(line+'\n')
                # split根据等号切片为前后两部分 字符串转列表
                line_attrs = line.strip().split('=')
                # 2.等号后为空则不翻译 写入输出文件
                if len(line_attrs) == 0:
                    print(line)
                    output_file.write(line+'\n')
                # 等号前面的键需要保留，后面的值需要翻译 join将列表拼接为字符串
                key = ''.join([_.strip() for _ in line_attrs[0]])
                value = ''.join([_.strip() for _ in line_attrs[1:]])
                # 3.文件名不翻译
                if value.endswith('.htm') or value.endswith('.HTM') or value.endswith('.html') or value.endswith('.HTML') or value.endswith('.gif') or value.endswith('.GIF'):
                    print(key+"="+value)
                    output_file.write(key+"="+value+'\n')
                # 4.正则表达式匹配标签，分开标签与文本，调用翻译，最后拼接结果
                result = getTranSentence(value)
                print(key+"="+result)
                output_file.write(key+"="+result+'\n')
    print ('***恭喜！翻译完成!***')
    print ('***翻译后的文件名称为：LocaleResource_zh_CN.properties***')
    input_file.close()
    output_file.close()

if __name__ == '__main__':
    main()
    
    