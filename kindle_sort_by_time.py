#coding=utf-8
import re
import os,os.path
import shutil
import random
import string
import time

BOUNDARY = u"==========\n" #分隔符
intab = "\/:*?\"<>|"
outtab = "  ： ？“《》 "     #用于替换特殊字符

HTML_HEAD = '''<!DOCTYPE html>
<html>
    <head>
    <meta charset="utf-8" />
    <title> 「 Kindle Notes 」 </title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="../style/css/bootstrap.min.css" rel="stylesheet" type="text/css" />
    <link href="../style/css/bootstrap-theme.min.css" rel="stylesheet" type="text/css" />
    <link href="../style/css/custom.css" rel="stylesheet" type="text/css" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Noto+Serif+SC">
    <link rel="icon" href="../images/bread.ico">
</head>
<body>
'''

INDEX_TITLE = '''
    <div class="container">
        <header class="header col-md-12">
            <div class="page-header">
                <h1><small><span class="glyphicon glyphicon-book" aria-hidden="true"></span> 「 参宿上 」 读书笔记 </small> <span class="badge">更新于 UPDATE </span> <span class="badge"> 共 BOOKS_SUM 本书，SENTENCE_SUM 条笔记</span></h1>
            </div>
        </header>
    <div class="col-md-12">
        <div class="list-group">

'''

BOOK_TITLE = '''
    <div class="container">
        <header class="header col-md-12">
            <div class="page-header">
                <h1><small><span class="glyphicon glyphicon-book" aria-hidden="true"></span>BookName</small> <span class="badge"></span></h1>
            </div>
        </header>

        <div class="col-md-2">
            <ul class="nav nav-pills nav-stacked">
                <li role="presentation" class="active text-center">
                    <a href="../index.html"><span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span> 返回目录</a>
                </li>
            </ul>
        </div>
'''

SENTENCE_CONTENT = '''
        <div class="col-md-12">
            <article>
                <div class="panel panel-default">
                    <div class="panel-body mk88"><p>SENTENCE_TXT
                    </p></div>
                    <div class="panel-footer text-right">
                        <span class="label label-primary"><span class="glyphicon glyphicon-tag" aria-hidden="true"></span> 标注</span>
                        <span class="label label-default"><span class="glyphicon glyphicon-bookmark" aria-hidden="true"></span>SENTENCE_ADDR</span>
                        <span class="label label-default"><span class="glyphicon glyphicon-time" aria-hidden="true"></span>SENTENCE_TIME</span>
                    </div>
                </div>
            </article>
        </div>
'''

ITEM_CONTENT = '''          <a href="HTML_URL" class="list-group-item"><span class="glyphicon glyphicon-book" aria-hidden="true"></span>HTML_FILE_NAME<span class="glyphicon glyphicon-tag" aria-hidden="true">SENTENCE_COUNT</span></a>
'''

FOOTER_CONTENT = '''
        </div>
    </div>
</body>
</html>
'''

def changechar(s):
    return s.translate(str.maketrans(intab,outtab))

def getAddr(s):
    g = s.split(" | ")[0]
    return g

def getTime(s):
    g = s.split(" | ")[1]
    return g.split("\n\n")[0]

def getMark(s):
    g = s.split(" | ")[1]
    try:
        return g.split("\n\n")[1]
    except IndexError:
        return "empty content"

f = open("source.txt", "r", encoding='utf-8')
content = f.read()
content = content.replace(u'\ufeff', u'')
clips = content.split(BOUNDARY)

print("列表个数：",clips.__len__())
sum = clips.__len__()

both = []
books = []
sentence = []
for i in range(0,sum):
    book = clips[i].split("\n-")
    both.append(book)
    if (book != ['']):
        books.append(changechar(book[0]))
        sentence.append(book[1])
print('笔记总数：',sentence.__len__())

nameOfBooks = list(set(books))
nameOfBooks.sort(key=books.index)
print('书籍总数：',nameOfBooks.__len__())

stceOfBookCnt = {}
book_latest_time = {}  # ⭐ 新增：每本书的最新阅读时间

if os.path.exists('books'):
    shutil.rmtree('books')
os.mkdir('books')
os.chdir('books')

for j in range(0,nameOfBooks.__len__()):
    if nameOfBooks[j].__len__() > 80:
        nameOfBooks[j] = nameOfBooks[j][0:80]

    f = open(nameOfBooks[j]+".html",'w',encoding='utf-8')
    f.write(HTML_HEAD)
    f.write(BOOK_TITLE.replace('BookName',nameOfBooks[j]))
    f.close()

    stceOfBookCnt[nameOfBooks[j]] = 0
    book_latest_time[nameOfBooks[j]] = "1900-01-01 00:00:00"  # 初始默认时间

file_list = os.listdir(".")
for j in range(0,sentence.__len__()):
    temp = both[j]
    filename = changechar(temp[0][0:80])
    if (filename+".html" in file_list ):
        s1 = getAddr(temp[1])
        s2 = getTime(temp[1])
        s3 = getMark(temp[1])
        f = open(filename+".html",'a',encoding='utf-8')
        if (s3 != '\n'):
            stceOfBookCnt[filename] += 1
            # ⭐ 记录该书最新阅读时间（保留更晚的）
            if s2 > book_latest_time[filename]:
                book_latest_time[filename] = s2
            f.write(SENTENCE_CONTENT.replace("SENTENCE_TXT",s3)
                                    .replace("SENTENCE_TIME",s2)
                                    .replace("SENTENCE_ADDR",s1))
        f.close()

for i in range(len(file_list)):
    f = open(file_list[i],'a',encoding='utf-8')
    f.write(FOOTER_CONTENT)
    f.close()

os.chdir("../")
f=open("index.html",'w',encoding='utf-8')
f.write(HTML_HEAD.replace("../",""))
f.write(INDEX_TITLE.replace("SENTENCE_SUM",str(sentence.__len__()))
                   .replace("UPDATE",time.strftime("%Y-%m-%d %H:%M", time.localtime()))
                   .replace("BOOKS_SUM",str(nameOfBooks.__len__())))

# ⭐ 构造 book_list 并按最新阅读时间排序
book_list = []
for file in os.listdir("books"):
    html_name = file.replace(".html",'')
    html_url = "books/" + file
    count = stceOfBookCnt.get(html_name, 0)
    latest_time = book_latest_time.get(html_name, "1900-01-01 00:00:00")
    book_list.append([html_url, html_name, count, latest_time])

# ⭐ 按时间倒序排序（最新阅读在前）
book_list.sort(key=lambda x: x[3], reverse=True)

# 写入HTML
for item in book_list:
    f.write(ITEM_CONTENT.replace("HTML_URL",item[0])
                        .replace("HTML_FILE_NAME",item[1])
                        .replace("SENTENCE_COUNT",str(item[2])))

f.write(FOOTER_CONTENT)
f.close()
