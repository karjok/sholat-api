from flask import Flask, request as req, render_template
from requests import get
from bs4 import BeautifulSoup as bs
import re

app = Flask(__name__)

@app.route("/")
def index():
	kota = get_city()["result"]
	return render_template("index.html",city=kota)
	
@app.route("/jadwal")
def jadwal():
    try:
        id = req.args["id_kota"]
        mode = req.args["mode"]
        id_kota = [i["id"] for i in get_city()["result"]]
        if str(id) in id_kota:
            result = get_schedule(city=id,mode=mode)
        else:
            result = {"success":False,"debug_message":f"kota dengan ID '{id}' tidak ditemukan. Periksa daftar ID kota di endpoint '/kota'"}
    except Exception as error:
        result = {"success":False,"debug_message":"paramenter 'id_kota' & 'mode' diperlukan"}
    return result
    
@app.route("/kota")
def kota():
    result = get_city()
    return result
# default untuk kota adalah 308 (jakarta pusat)
def get_schedule(city=308,mode="daily"):
	try:
		r = get('https://www.jadwalsholat.org/adzan/monthly.php?id=30')
		b = bs(r.text,'html.parser')

		title = "Tanggal Imsyak Shubuh Terbit Dhuha Dzuhur Ashr Maghrib Isya".lower().split()
		city = b.find('option', attrs={'value':city})
		result = {"kota":city.text}

		if mode == "daily":
			tr = b.find('tr',class_="table_highlight")
			td_tag = [x.text for x in tr.find_all('td')]
			data = dict(zip(title,td_tag))
			result["data"] = data
			ret = {"success":True,"debug_message":"ok","result":result}
		elif mode == "monthly":
			pattern = r"<b>(\d+)</b>.*?<td>(\d+:\d+)</td><td>(\d+:\d+)</td><td>(\d+:\d+)</td><td>(\d+:\d+)</td><td>(\d+:\d+)</td><td>(\d+:\d+)</td><td>(\d+:\d+)</td><td>(\d+:\d+)</td>"
			tr = re.findall(pattern,r.text)
			data = []
			for day in tr:
				sched = dict(zip(title,day))
				data.append(sched)
			result["data"] = data
			ret = {"success":True,"debug_message":"ok","result":result}
		else:
		    ret = {"success":False,"debug_message":f"Mode '{mode}' tidak diketahui, cek daftar paramenter di halaman depan"}
	except Exception as error:
		ret = {"success":False,"debug_message":str(error)}
	return ret

def get_city():
	try:
		u = "https://www.jadwalsholat.org/adzan/monthly.php"
		r = get(u).text
		b = bs(r,"html.parser")
		result = [{"kota":i.text.lower(),"id":i["value"]} for i in b.find_all("option")]
		ret = {"success":True,"debug_message":"ok","result":result}
	except Exception as error:
		ret = {"success":True,"debug_message":str(error)}
	return ret