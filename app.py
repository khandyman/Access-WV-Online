#!/usr/bin/env python3
import argparse
from database import retrieve_records
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import pty
import os
import subprocess
import socket
import select
import termios
import struct
import fcntl
import shlex
import logging
import sys

logging.getLogger("werkzeug").setLevel(logging.ERROR)

__version__ = "0.5.0.2"

app = Flask(__name__, template_folder="./templates", static_folder="./static", static_url_path="")
app.config["SECRET_KEY"] = "secret!"
app.config["fd"] = None
app.config["child_pid"] = None
socketio = SocketIO(app)


def set_winsize(fd, row, col, xpix=0, ypix=0):
    logging.debug("setting window size with termios")
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def read_and_forward_pty_output():
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        if app.config["fd"]:
            timeout_sec = 0
            (data_ready, _, _) = select.select([app.config["fd"]], [], [], timeout_sec)
            if data_ready:
                output = os.read(app.config["fd"], max_read_bytes).decode(
                    errors="ignore"
                )
                socketio.emit("pty-output", {"output": output}, namespace="/pty")


@app.route("/")
def log_in():
    return render_template("log_in.html")


@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


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


@app.route('/host_names/<network_element>/<wire_center>', methods=['GET', 'POST'])
def host_names(network_element, wire_center):
    query = (f"SELECT host_names.clli FROM host_names " 
             "INNER JOIN wire_centers ON wire_centers.abbr = host_names.location " 
             f"WHERE host_names.type = '{network_element}' AND wire_centers.name = '{wire_center}'"
             "ORDER BY host_names.clli")

    host_names_list = retrieve_records(query)

    return render_template('host_names.html',
                           network_element=network_element, wire_center=wire_center, host_names=host_names_list)


@app.route('/search', methods=['POST'])
def search():
    search_string = request.form['search_bottom']
    query = f"SELECT clli FROM host_names WHERE clli LIKE '%{search_string}%'"
    host_names_list = retrieve_records(query)

    return render_template('host_names.html',
                            network_element=search_string, wire_center=search_string,
                            host_names=host_names_list)


@app.route('/search_top', methods=['POST'])
def search_top():
    search_string = request.form['search_top']
    query = f"SELECT clli FROM host_names WHERE clli LIKE '%{search_string}%'"
    host_names_list = retrieve_records(query)

    return render_template('host_names.html',
                            network_element=search_string, wire_center=search_string,
                            host_names=host_names_list)


@app.route('/device_connection/<network_element>/<wire_center>/<clli>')
def device_connection(network_element, wire_center, clli):
    query = f"SELECT ip, port FROM host_names WHERE clli = '{clli}'"
    connect_list = retrieve_records(query)

    return render_template('device_connection.html',
                           network_element=network_element, wire_center=wire_center,
                           ip=connect_list[0]['ip'], port=connect_list[0]['port'])


@app.route('/back')
def back():
    return render_template('host_names.html',
                           network_element='none', wire_center='none', host_names='none')


@app.route("/<ip>/<port>")
def connect(ip, port):
    return render_template("connect.html", ip=ip, port=port)


@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    """write to the child pty. The pty sees this as if you are typing in a real
    terminal.
    """
    if app.config["fd"]:
        logging.debug("received input from browser: %s" % data["input"])
        os.write(app.config["fd"], data["input"].encode())


@socketio.on("resize", namespace="/pty")
def resize(data):
    if app.config["fd"]:
        logging.debug(f"Resizing window to {data['rows']}x{data['cols']}")
        set_winsize(app.config["fd"], data["rows"], data["cols"])


@socketio.on("connect", namespace="/pty")
def connect():
    """new client connected"""
    logging.info("new client connected")
    if app.config["child_pid"]:
        # already started child process, don't start another
        return

    # create child process attached to a pty we can read from and write to
    (child_pid, fd) = pty.fork()
    if child_pid == 0:
        # this is the child process fork.
        # anything printed here will show up in the pty, including the output
        # of this subprocess
        subprocess.run(app.config["cmd"])
    else:
        # this is the parent process fork.
        # store child fd and pid
        app.config["fd"] = fd
        app.config["child_pid"] = child_pid
        set_winsize(fd, 50, 50)
        cmd = " ".join(shlex.quote(c) for c in app.config["cmd"])
        # logging/print statements must go after this because... I have no idea why
        # but if they come before the background task never starts
        socketio.start_background_task(target=read_and_forward_pty_output)

        logging.info("child pid is " + child_pid)
        logging.info(
            f"starting background task with command `{cmd}` to continously read "
            "and forward pty output to client"
        )
        logging.info("task started")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "A fully functional terminal in your browser. "
            "https://github.com/cs01/pyxterm.js"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-p", "--port", default=5000, help="port to run server on", type=int
    )

    host_name = socket.gethostname()

    if 'awv' in host_name or 'accesswv' in host_name:
        host_ip = "0.0.0.0"
    else:
        host_ip = "127.0.0.1"

    parser.add_argument(
        "--host",
        default=host_ip,
        help="host to run server on (use 0.0.0.0 to allow access from other hosts)",
    )

    parser.add_argument("--debug", action="store_true", help="debug the server")
    parser.add_argument("--version", action="store_true", help="print version and exit")
    parser.add_argument(
        "--command", default="bash", help="Command to run in the terminal"
    )
    parser.add_argument(
        "--cmd-args",
        default="",
        help="arguments to pass to command (i.e. --cmd-args='arg1 arg2 --flag')",
    )
    args = parser.parse_args()
    if args.version:
        print(__version__)
        exit(0)
    app.config["cmd"] = [args.command] + shlex.split(args.cmd_args)
    green = "\033[92m"
    end = "\033[0m"
    log_format = (
        green
        + "pyxtermjs > "
        + end
        + "%(levelname)s (%(funcName)s:%(lineno)s) %(message)s"
    )
    logging.basicConfig(
        format=log_format,
        stream=sys.stdout,
        level=logging.DEBUG if args.debug else logging.INFO,
    )
    logging.info(f"serving on http://{args.host}:{args.port}")
    socketio.run(app, debug=args.debug, port=args.port, host=args.host, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
