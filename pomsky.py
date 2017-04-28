#!/usr/bin/env python
# -- coding: utf-8 --
"""pomsky v0.0.1
usage: python pomsky.py [options]
Available options are:
  -h        prints help
  -w<FILE>  sets the workingfile, default: /tmp/pomsky.txt
  -p<PORT>  changes the port, default: 8888
  -d<DEBUG> sets the debug command, default: "du -h *"
  -a#<CMD>  sets a command a0 to a9 are free slots to define commands
            default: "ls > /dev/null"
  -v        verbose mode

Example:
    python pomsky.py -w"top.dat" -a0"ps -ax > top.dat" -a1"ls > top.dat"
"""
import os
import socket
import sys

try:
    # Python 2.x
    from urllib import unquote_plus
    from commands import getstatusoutput as execute
except Exception:
    # Python 3.x
    from urllib.parse import unquote_plus
    from subprocess import getstatusoutput as execute

# default values
port, workingfile, debug_cmd, verbose = 8888, "/tmp/pomsky.txt", "du -h *", False
additional_cmds = {"0": "ls > /dev/null"}

# arg parsing
for cwd in sys.argv:
    if cwd.startswith("-h"):
        print(__doc__)
        exit(0)
    if cwd.startswith("-w"):
        workingfile = cwd[2:]
    if cwd.startswith("-p"):
        port = int(cwd[2:])
    if cwd.startswith("-d"):
        debug_cmd = cwd[2:]
    if cwd.startswith("-a") and len(cwd) > 2:
        if cwd[2].isdigit():
            additional_cmds.update({cwd[2]: cwd[3:]})
    if cwd.startswith("-v"):
        verbose = True

# prepare workingfile
if not os.path.isfile(workingfile):
    os.mknod(workingfile)

# create list of html buttons
cmd_buttons = '\n'.join(map(lambda link:
                            """<a href="/run%s" target="_blank"><button>Run %s</button></a>""" % (link[0], link[1]),
                            additional_cmds.items()))

# open socket
HOST, PORT = '', port
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)

def read_content_file():
    """ Read working file """

    f = open(workingfile, "r")
    content = f.read()
    f.close()

    if hasattr(content, "decode"):
        return str(content.decode("utf-8"))
    else:
        return str(content)

def write_content_file(file_content):
    """ Write new working file """

    f = open(workingfile, "w")
    f.write(str(file_content))
    f.close()

def handle_request(request):
    """ Executes some programms
        TODO: Handle routes!!
    """

    args = request.decode("utf-8").split()
    header_line = args[0].lower()

    is_get = header_line.startswith("get")
    is_post = header_line.startswith("post")
    #import ipdb; ipdb.set_trace()
    if is_get and str(args[1]).startswith("/run"):
        cmd_number = str(args[1])[4]
        os.system("%s &" % additional_cmds[cmd_number])

    if is_post:
        body = request.decode("utf-8").split("\r\n\r\n")[1]
        if body.startswith("input="):
            write_content_file(unquote_plus(body[6:]).encode("utf-8"))




def create_response(content, debug, debug_cmd, cmd_buttons=cmd_buttons):
    """ Creates the http response """
    return """\
HTTP/1.1 200 OK
Content-Type: text/html

<html>
<form action="/" method="post">
<textarea name="input" style="width:100%%;height:25%%;" placeholder="%(workingfile)s">%(content)s</textarea>
<input type="submit" value="Submit">
</form>
<hr />
%(cmd_buttons)s
<hr />
<h3>Debug (%(debug_cmd)s):</h3>
<pre>%(debug)s</pre>
</html>""" % {"content": content,
              "debug": debug,
              "debug_cmd": debug_cmd,
              "cmd_buttons": cmd_buttons,
              "workingfile": workingfile}

import time
benchmark = []
def main():
    """ Entry-point with REPL """
    print("Serving pomsky on 0.0.0.0 port %s ..." % PORT)
    if verbose:
        print('staring pomsky...\nport:\t\t%s\nworkingfile:\t%s\ncommand:\t%s\ndebug:\t\t%s' % (
    PORT, workingfile, additional_cmds, debug_cmd))
    while True:
        try:
            try:
                client_connection, client_address = listen_socket.accept()
                request = client_connection.recv(2*1024*1024)
                start = time.time()

                if verbose:
                    print(request.decode("utf-8"))

                handle_request(request)
                ret, debug = execute(debug_cmd)

                http_response = create_response(read_content_file(), debug, debug_cmd)

                client_connection.sendall(http_response.encode('utf-8'))
                end = (time.time()-start)*1000
                benchmark.append(end)

                if verbose:
                    print("time: %s" % (end))
                    print("benchmark mean= %s" % (sum(benchmark)/len(benchmark)))
                    print("benchmark min= %s" % (min(benchmark)))
                    print("benchmark max= %s" % (max(benchmark)))
            except Exception:
                e = sys.exc_info()[1]
                print(e.args[0])
        finally:
            client_connection.close()

if __name__ == "__main__":
    main()
