from flask import Flask, render_template, request
from database import retrieve_records

app = Flask(__name__)

wire_centers_list = [
    {
        'id:': 0,
        'name': 'Beckley'
    },
    {
        'id:': 1,
        'name': 'Charleston'
    },
    {
        'id:': 2,
        'name': 'Clarksburg'
    },
    {
        'id:': 3,
        'name': 'Logan'
    },
    {
        'id:': 4,
        'name': 'Martinsburg'
    },
    {
        'id:': 5,
        'name': 'Morgantown'
    },
    {
        'id:': 6,
        'name': 'Parkersburg'
    },
    {
        'id:': 7,
        'name': 'Weirton'
    },
    {
        'id:': 8,
        'name': 'Wheeling'
    },
    {
        'id:': 9,
        'name': 'Williamson'
    },
]


@app.route('/')
def log_in():
    return render_template('log_in.html')


@app.route('/network_elements')
def network_elements():
    query = "SELECT * FROM network_elements"
    network_elements_list = retrieve_records(query)

    return render_template('network_elements.html',
                           network_elements=network_elements_list)


@app.route('/wire_centers/<device_type>')
def wire_centers(device_type):
    query = (f"SELECT DISTINCT wire_centers.name FROM wire_centers "
             "INNER JOIN host_names ON wire_centers.abbr = host_names.location " 
             "INNER JOIN network_elements ON network_elements.name = host_names.type "
             f"WHERE host_names.type = '{device_type}'")
    wire_center_list = retrieve_records(query)

    return render_template('wire_centers.html',
                           wire_centers=wire_center_list)


@app.route('/host_names')
def host_names():
    return render_template('host_names.html')


@app.route('/device_connection')
def device_connection():
    return render_template('device_connection.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)