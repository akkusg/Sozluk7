import base64
import datetime
from flask import Flask, render_template, request, redirect, session
import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'bizim cok zor gizli sozcugumuz'

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["sozluk7DB"]
kullanicilar_tablosu = mydb["kullanicilar"]
basliklar_tablosu = mydb["basliklar"]
yazilar_tablosu = mydb["yazilar"]

@app.route('/')
def baslangic():
    basliklar = basliklar_tablosu.find({})
    yazilar = yazilar_tablosu.find({})

    return render_template("anasayfa.html", basliklar=basliklar, yazilar=yazilar)


if __name__ == "__main__":
    app.run(debug=True)