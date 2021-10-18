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
    basliklar = basliklar_tablosu.find({}).sort([("_id",pymongo.DESCENDING)])
    yazilar = yazilar_tablosu.find({})
    kayit = None
    if 'kullanici' in session:
        kayit = session["kullanici"]

    return render_template("anasayfa.html", kullanici=kayit, basliklar=basliklar, yazilar=yazilar)



@app.route('/b/<baslik_id>')
def baslik_goster(baslik_id):
    kullanici = None
    baslik = None
    basliklar = basliklar_tablosu.find({}).sort([("_id",pymongo.DESCENDING)])
    yazilar=[]
    if 'kullanici' in session:
        kullanici = session["kullanici"]
    if baslik_id:
        baslik = basliklar_tablosu.find_one({"_id": ObjectId(baslik_id)})
        print(ObjectId(baslik_id))
        yazilar = yazilar_tablosu.find({"baslik._id": ObjectId(baslik_id)}).sort([("_id",pymongo.DESCENDING)])
        yazilar_tablosu.find({})
        print(yazilar)
    return render_template("baslikgoster.html", kullanici=kullanici, baslik=baslik, basliklar=basliklar, yazilar=yazilar)



@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        kullanici = request.form['kullanici']
        sifre = request.form['sifre']
        kayit = kullanicilar_tablosu.find_one({"_id": kullanici})
        if kayit:
            if sifre == kayit["sifre"]:
                del kayit['sifre']
                session["kullanici"] = kayit
                return redirect("/", code=302)
            else:
                return "Şifre yanlış"
        else:
            return "Kullanıcı bulunamadı"
    else:
        return render_template("giris.html")


@app.route('/yenibaslik', methods=['GET', 'POST'])
def yeni_baslik():
    if request.method == 'POST':
        baslik = request.form['baslik']
        kayit = {"metin": baslik}
        basliklar_tablosu.insert_one(kayit)
        return redirect("/", code=302)

    else:
        return render_template("yenibaslik.html")


@app.route('/yeniyazi/<baslik_id>', methods=['GET', 'POST'])
def yeni_yazi(baslik_id):
    baslik = basliklar_tablosu.find_one({"_id": ObjectId(baslik_id)})
    if request.method == 'POST':
        yazi = request.form['yazi']
        kullanici = session["kullanici"]
        kayit={"baslik": baslik, "icerik": yazi, "paylasim_tarihi": datetime.datetime.now(), "kullanici": kullanici}
        yazilar_tablosu.insert_one(kayit)
        return redirect("/b/" + baslik_id, code=302)

    else:
        return render_template("yeniyazi.html", baslik = baslik)


@app.route('/cikis')
def cikis():
    session.clear()
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)