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

@app.route('/')
def log_in():
    return render_template('log_in.html')

@app.route('/network_elements')
def network_elements():
    return render_template('network_elements.html',
                           network_elements=network_elements_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)