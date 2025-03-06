import csv
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load CSV data into memory (only once) and store it in a list
def load_data(filename):
    with open(filename, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter='\t')  # Using tab as delimiter
        headers = next(csv_reader)  # Assuming first row is header
        data = []
        for row in csv_reader:
            item = {
                "sn": row[0],  # Replace 'id' with 'sn' (serial number)
                "name": row[1],
                "price": row[2],
                "quantity": row[3],
                "discount": row[4],
                "tax": row[5],
                "other_info": row[6],
                "value": row[7],
                "price_value": row[8],
                "brand": row[9],
                "code": row[10]  # Assuming 'code' is a separate field
            }
            data.append(item)
    return data

# Load all data
data = load_data('LE.txt')

# Function to apply filtering
def filter_data(data, filters):
    filtered_data = data
    for key, value in filters.items():
        if key in ["name", "sn", "code"]:  # Filtering by 'name', 'sn', or 'code'
            filtered_data = [item for item in filtered_data if value.lower() in item[key].lower()]
    return filtered_data

# Function to sort data
def sort_data(data, sort_by, reverse=False):
    return sorted(data, key=lambda x: x.get(sort_by, ''), reverse=reverse)

# Function to paginate data
def paginate_data(data, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    return data[start:end]

@app.route('/spare-parts', methods=['GET'])
def spare_parts():
    # Get query parameters
    page = int(request.args.get('page', 1))  # Default to page 1
    per_page = int(request.args.get('per_page', 10))  # Default to 10 items per page
    name_filter = request.args.get('name')  # Filtering by name
    sn_filter = request.args.get('sn')  # Filtering by sn (serial number)
    sort_by = request.args.get('sort')  # Sorting by a column
    reverse = False
    
    # If sorting in reverse
    if sort_by and sort_by.startswith('-'):
        sort_by = sort_by[1:]
        reverse = True

    # Apply filters
    filters = {}
    if name_filter:
        filters['name'] = name_filter
    if sn_filter:
        filters['sn'] = sn_filter  # Filtering by sn (serial number)

    filtered_data = filter_data(data, filters)

    # Sort data
    if sort_by:
        filtered_data = sort_data(filtered_data, sort_by, reverse)

    # Paginate data
    paginated_data = paginate_data(filtered_data, page, per_page)

    # Return the JSON response
    return jsonify(paginated_data)

@app.route('/spare-parts/search/<string:query>', methods=['GET'])
def search_spare_parts(query):
    page = int(request.args.get('page', 1))  # Default to page 1
    per_page = int(request.args.get('per_page', 10))  # Default to 10 items per page

    # Filter by search query (default is searching by 'name')
    filters = {'name': query}
    filtered_data = filter_data(data, filters)

    # Paginate data
    paginated_data = paginate_data(filtered_data, page, per_page)

    return jsonify(paginated_data)

if __name__ == '__main__':
    app.run(debug=True, port=3300)
