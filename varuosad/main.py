import csv
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# laeb CSV andmed mällu ja salvestab need nimekirja
def load_data(filename):
    with open(filename, mode='r', encoding='utf-8') as file:  # Avab faili lugemiseks
        csv_reader = csv.reader(file, delimiter='\t')  # Kasutame tabi CSV failis
        headers = next(csv_reader)  # Eeldame, et esimene rida on päis
        data = []  # Loome tühja nimekirja, kuhu salvestame andmed
        for row in csv_reader:  # Läbime kõik read, välja arvatud päis
            item = {  # Loome sõnastiku, mis sisaldab iga veeru väärtusi
                "sn": row[0],  # seerianumber
                "name": row[1],  # nimi
                "price": row[2],  # hind
                "quantity": row[3],  # kogus
                "discount": row[4],  # soodustus
                "tax": row[5],  # maks
                "other_info": row[6],  # muu info
                "value": row[7],  # 'väärtus
                "price_value": row[8],  # hinna väärtus
                "brand": row[9],  # brändi nimi
                "code": row[10]  # kood
            }
            data.append(item)  # Lisame selle sõnastiku andmete nimekirja
    return data  # Tagastame kogu andmete nimekirja

# Laeme kõik andmed
data = load_data('LE.txt')  # Laeb andmed faili 'LE.txt'

# Funktsioon andmete filtreerimiseks
def filter_data(data, filters):
    filtered_data = data  # Alustame kogu andmete nimekirjast
    for key, value in filters.items():  # Läbime kõik filtrid, mis on määratud
        if key in ["name", "sn", "code"]:  # Filtreerime ainult 'name', 'sn' või 'code' järgi
            filtered_data = [item for item in filtered_data if value.lower() in item[key].lower()]  # Filtreerimine väikeste tähtedega
    return filtered_data  # Tagastame filtreeritud andmed

# Funktsioon andmete sorteerimiseks
def sort_data(data, sort_by, reverse=False):
    return sorted(data, key=lambda x: x.get(sort_by, ''), reverse=reverse)  # Sorteerib andmed valitud veeru järgi

# Funktsioon andmete lehekülgedele jagamiseks
def paginate_data(data, page, per_page):
    start = (page - 1) * per_page  # Arvutab, millest alustada
    end = start + per_page  # Arvutab, kus lõppeda
    return data[start:end]  # Tagastab andmed vastavalt leheküljekogusele

@app.route('/spare-parts', methods=['GET'])
def spare_parts():
    # Saame päringu parameetrid URL-ist
    page = int(request.args.get('page', 1))  # Vaikimisi on lehekülg 1
    per_page = int(request.args.get('per_page', 10))  # Vaikimisi on 10 elementi leheküljel
    name_filter = request.args.get('name')  # Nime järgi filtreerimine
    sn_filter = request.args.get('sn')  # Seerianumbri järgi filtreerimine
    sort_by = request.args.get('sort')  # Sorteerimine veeru järgi
    reverse = False  # Alguses ei sorteerita vastupidises järjekorras
    
    # sorteerimine vastupidises järjekorras
    if sort_by and sort_by.startswith('-'):  # Kui sorteerimisveerg algab miinusega
        sort_by = sort_by[1:]  # Eemaldame miinuse
        reverse = True  # Seame vastupidise järjekorra

    # Rakendame filtrid
    filters = {}
    if name_filter:  # Kui päringus on määratud nimi
        filters['name'] = name_filter
    if sn_filter:  # Kui päringus on määratud seerianumber
        filters['sn'] = sn_filter  # Filtreerime seerianumbri järgi

    filtered_data = filter_data(data, filters)  # Rakendame filtrid

    # Sorteerime andmed
    if sort_by:  # Kui on määratud, kuidas sorteerida
        filtered_data = sort_data(filtered_data, sort_by, reverse)

    # Teostame lehekülgedele jagamise
    paginated_data = paginate_data(filtered_data, page, per_page)

    # Tagastame JSON formaadis vastuse
    return jsonify(paginated_data)

@app.route('/spare-parts/search/<string:query>', methods=['GET'])
def search_spare_parts(query):
    page = int(request.args.get('page', 1))  # Vaikimisi on lehekülg 1
    per_page = int(request.args.get('per_page', 10))  # Vaikimisi on 10 elementi leheküljel

    # Filtreerime otsingupäringu järgi 
    filters = {'name': query}
    filtered_data = filter_data(data, filters)  # Rakendame filtrit

    # Teostame lehekülgedele jagamise
    paginated_data = paginate_data(filtered_data, page, per_page)

    return jsonify(paginated_data)  # Tagastame otsingutulemused JSON formaadis

if __name__ == '__main__':
    app.run(debug=True, port=3300)  # Käivitame Flask rakenduse
