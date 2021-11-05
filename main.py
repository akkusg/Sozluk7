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
    yazilar = yazilar_tablosu.find({}).sort([("_id",pymongo.DESCENDING)]).limit(5)
    kayit = None
    if 'kullanici' in session:
        kayit = session["kullanici"]

    return render_template("anasayfa.html", kullanici=kayit, basliklar=basliklar, yazilar=yazilar)



@app.route('/b/<baslik_id>/<sayfa_no>')
def baslik_goster(baslik_id, sayfa_no):
    kullanici = None
    baslik = None
    basliklar = basliklar_tablosu.find({}).sort([("_id",pymongo.DESCENDING)])
    yazilar=[]
    if 'kullanici' in session:
        kullanici = session["kullanici"]
    if baslik_id:
        sayfalama_offset = (int(sayfa_no) - 1) * 50
        baslik = basliklar_tablosu.find_one({"_id": ObjectId(baslik_id)})
        print(ObjectId(baslik_id))
        yazilar = list(yazilar_tablosu.find({"baslik._id": ObjectId(baslik_id)}).sort([("_id",pymongo.DESCENDING)]).skip(sayfalama_offset).limit(51))
        sonraki_sayfa_var = True
        sonraki_sayfa_no = int(sayfa_no) + 1
        onceki_sayfa_no = int(sayfa_no) - 1
        if len(yazilar) < 51:
            sonraki_sayfa_var = False
        else:
            yazilar.pop()


    return render_template("baslikgoster.html", kullanici=kullanici, baslik=baslik, basliklar=basliklar, yazilar=yazilar, sayfa_no=sayfa_no, sonraki_sayfa_var=sonraki_sayfa_var, sonraki_sayfa_no=sonraki_sayfa_no, onceki_sayfa_no=onceki_sayfa_no)



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



@app.route('/testyazisiolustur/<baslik_id>', methods=['GET'])
def test_yazi_olustur(baslik_id):
    for i in range(0,40000):
        baslik = basliklar_tablosu.find_one({"_id": ObjectId(baslik_id)})
        kullanici = session["kullanici"]
        yazi = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"
        yazi = "--" + str(i) + "--" + yazi
        kayit={"baslik": baslik, "icerik": yazi, "paylasim_tarihi": datetime.datetime.now(), "kullanici": kullanici}
        yazilar_tablosu.insert_one(kayit)
    return "yazılar oluşturuldu"




@app.route('/cikis')
def cikis():
    session.clear()
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)