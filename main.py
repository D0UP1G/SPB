from nltk.corpus import stopwords
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk import sent_tokenize
from nltk import word_tokenize
import sqlite3
from fastapi import FastAPI


marks = """\'"!&?№:;,-."""
stopwords = stopwords.words("russian")
stemmer = SnowballStemmer("russian")

answer = ""
questions = []
exclamations = []  # восклицания
sentences = []

def SortingSents(sentence: list[str]):
    for i in sentence:
        count = 0
        for j in i:
            if j in marks:
                if (j == '!'):
                    count = 1
                elif (j == '?'):
                    count = 2
                i = i.replace(j, "")
        if (count == 0):
            sentences.append(i)
        elif (count == 1):
            exclamations.append(i)
        else:
            questions.append(i)

def Zeroing(a:list[tuple])->list[int]:
    for i in range(len(a)):
        a[i] = 0
    return a

def SentenceToList(sentence: str) -> list[str]:
    return list(filter(None, sentence.lower().split(' ')))

def StopwordsClear(sentence:list[str]):#убирает стоп слова из всего questions
    for i in range(len(sentence)):
        b = word_tokenize(sentence[i])
        c=[]
        for j in b:
            if j not in stopwords and (j.lower() != "сколько"):
                j = stemmer.stem(j)
                c.append(j)
        sentence[i] =" ".join(c).lower()

def SQLConnect(connection)->sqlite3.Cursor:
    cursor = connection.cursor()
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY,
                tag1 TEXT,
                tag2 TEXT,
                tag3 TEXT,
                tag4 TEXT,
                tag5 TEXT,
                tag6 TEXT,
                tag7 TEXT,
                tag8 TEXT,
                tag9 TEXT,
                tag10 TEXT
            )''')
    
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY,
                answer TEXT
            )''')
    
    return cursor

async def ans(inp:str):
    global answer
    global questions
    global exclamations
    global sentences

    with sqlite3.connect("baker's.db") as connection:
        cursor = SQLConnect(connection)#конект к датабазе + создание таблиц
        userInput = inp
        answer+="Спасибо за отзыв. Ваше мнение очень важно для нас. "

        SortingSents(sent_tokenize(userInput))#распределение по спискам ввода пользователя
        StopwordsClear(questions)#очищает questions от стоп слов

        ids = Zeroing(cursor.execute("""SELECT id FROM tags""").fetchall())#список с количеством id 

        for i in questions:#на каком id больше тегов совпало
            for j in i.split():
                for k in range(1,len(ids)+1):
                    id = cursor.execute(f"""SELECT * FROM tags WHERE id LIKE {k}""").fetchall()
                    for l in id:
                        if j in l:
                            ids[k-1] +=1  
                            break
        if max(ids) != 0:
            indexMaxValue = ids.index(max(ids))
            answer += cursor.execute(f"""SELECT answer FROM answers WHERE id LIKE {indexMaxValue+1}""").fetchone()[0]
        else:
            answer = "Извините, но я не понял ваш впрос."
    
    return answer


app = FastAPI()

@app.post('/answer')
async def main(stri:str):
    return {
        'answer': await ans(stri)
    }