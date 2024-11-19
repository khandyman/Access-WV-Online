from flask import Flask, render_template

app = Flask(__name__)

network_elements_list = [
    {
        'id': 0,
        'name': '7210'
    },
    {
        'id': 1,
        'name': '7450'
    },
    {
        'id': 2,
        'name': 'Actelis'
    },
    {
        'id': 3,
        'name': 'Ciena'
    },
    {
        'id': 4,
        'name': 'Cordell'
    },
    {
        'id': 5,
        'name': 'DDM'
    },
    {
        'id': 6,
        'name': 'FLM'
    },
    {
        'id': 7,
        'name': 'FT2000'
    },
    {
        'id': 8,
        'name': 'Litespan'
    },
    {
        'id': 9,
        'name': 'ME3600'
    },
    {
        'id': 10,
        'name': 'TA3000'
    },
    {
        'id': 11,
        'name': 'TM50'
    }
]

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
    return render_template('network_elements.html',
                           network_elements=network_elements_list)

@app.route('/wire_centers')
def wire_centers():
    return render_template('wire_centers.html',
                           wire_centers=wire_centers_list)

@app.route('/host_names')
def host_names():
    return render_template('host_names.html')

@app.route('/device_connection')
def device_connection():
    return render_template('device_connection.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)