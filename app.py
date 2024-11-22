from flask import Flask, render_template, request
from database import retrieve_records

app = Flask(__name__)


@app.route('/')
def log_in():
    return render_template('log_in.html')


@app.route('/home')
def home():
    return render_template('home.html')

# @app.route('/network_elements')
# def network_elements():
#     query = "SELECT * FROM network_elements"
#     network_elements_list = retrieve_records(query)
#
#     return render_template('network_elements.html', network_elements=network_elements_list)


@app.route('/network_elements/<wire_center>')
def network_elements(wire_center):
    if wire_center == 'none':
        query = f"SELECT network_elements.name FROM network_elements"
    else:
        query = (f"SELECT DISTINCT network_elements.name FROM network_elements "
                "INNER JOIN host_names ON network_elements.name = host_names.type " 
                "INNER JOIN wire_centers ON host_names.location = wire_centers.abbr "
                f"WHERE wire_centers.name = '{wire_center}' ORDER BY network_elements.name ")

    network_elements_list = retrieve_records(query)

    return render_template('network_elements.html',
                           wire_center=wire_center, network_elements=network_elements_list)


# @app.route('/wire_centers')
# def wire_centers():
#     query = "SELECT * FROM wire_centers"
#     wire_centers_list = retrieve_records(query)
#
#     return render_template('wire_centers.html', wire_centers=wire_centers_list)


@app.route('/wire_centers/<network_element>')
def wire_centers(network_element):
    if network_element == 'none':
        query = f"SELECT wire_centers.name FROM wire_centers"
    else:
        query = (f"SELECT DISTINCT wire_centers.name FROM wire_centers "
                 "INNER JOIN host_names ON wire_centers.abbr = host_names.location "
                 "INNER JOIN network_elements ON host_names.type = network_elements.name "
                 f"WHERE host_names.type = '{network_element}' ORDER BY wire_centers.name")
    wire_center_list = retrieve_records(query)

    return render_template('wire_centers.html',
                           network_element=network_element, wire_centers=wire_center_list)


@app.route('/host_names/<network_element>/<wire_center>')
def host_names(network_element, wire_center):
    query = (f"SELECT host_names.clli FROM host_names " 
             "INNER JOIN wire_centers ON wire_centers.abbr = host_names.location " 
             f"WHERE host_names.type = '{network_element}' AND wire_centers.name = '{wire_center}'"
             "ORDER BY host_names.clli")
    host_names_list = retrieve_records(query)

    return render_template('host_names.html',
                           network_element=network_element, wire_center=wire_center, host_names=host_names_list)


@app.route('/device_connection/<network_element>/<wire_center>/<clli>')
def device_connection(network_element, wire_center, clli):


    return render_template('device_connection.html',
                           network_element=network_element, wire_center=wire_center, clli=clli)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)