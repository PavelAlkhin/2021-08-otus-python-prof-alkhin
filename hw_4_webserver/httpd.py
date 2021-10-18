import logging
import socket
import threading
from optparse import OptionParser

# allgo = threading.Condition()


class WebServer:
    def __init__(self, bind_ip, bind_port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((bind_ip, bind_port))
        self.server.listen(5)  # max backlog of connections
        self.bind_ip = bind_ip
        self.bind_port = bind_port


class HTTPError(Exception):
    def __init__(self, status, reason, body=None):
        super()
        self.status = status
        self.reason = reason
        self.body = body


def parse_request_line(raw):
    words_list = raw.split()
    data = {}
    count_w = len(words_list)
    if count_w == 0:
        raise HTTPError(400, 'Bad request',
                        f'Malformed request line{raw}')

    for i in range(0, count_w - 1):
        word = words_list[i]
        if word == 'GET' or word == 'POST':
            data['method'] = word
            data['resource'] = words_list[i + 1]
        if 'HTTP' in word:
            data['version'] = word
        if 'Cookie' in word:
            data['cookie'] = words_list[i + 1]

    if data['version'] != 'HTTP/1.1':
        raise HTTPError(505, 'HTTP Version Not Supported')
    return data


def handle_client_connection(client_socket):
    request = client_socket.recv(1024)
    logging.info(f'Received {request}')
    request_data = request.decode()
    req_get, other = request_data.split('HTTP/')
    req_g, path = req_get.split('GET ')

    path = path.replace(' ', '')

    if '.' not in path:
        c = len(path)
        if path[:c - 1] != '/':
            path += '/'
        path += 'index.html'
    index_file = f'.{path}'
    try:
        with open(index_file, 'rb') as f:  # open file , r => read , b => byte format
            response = f.read()

        header = 'HTTP/1.1 200 OK\n'

        if index_file.endswith(".jpg"):
            mimetype = 'image/jpg'
        elif index_file.endswith(".css"):
            mimetype = 'text/css'
        else:
            mimetype = 'text/html'

        header += 'Content-Type: ' + str(mimetype) + '\n\n'

    except Exception as e:
        header = 'HTTP/1.1 404 Not Found\n\n'
        response = 'f<html><body><center><h3>Error 404: Resourse not found</h3><p>Python HTTP ' \
                   'Server</p></center></body></html>'.encode('utf-8')
        logging.exception(f'exception {e}')

    final_response = header.encode('utf-8')
    logging.info(f'header: {final_response}')

    final_response += response
    client_socket.send(final_response)
    client_socket.close()


class ThreadClass(threading.Thread):

    def __init__(self, web_server):
        self.server = web_server
        super().__init__()

    def run(self):
        logging.info(f'Listening on {self.server.bind_ip}:{self.server.bind_port}')

        while True:
            client_sock, address = self.server.server.accept()
            logging.info(f'Accepted connection from {address[0]}:{address[1]}')
            client_handler = threading.Thread(
                target=handle_client_connection,
                args=(client_sock,)
            )
            client_handler.start()
        serv_sock.close()

        # allgo.acquire()
        # allgo.wait()
        # allgo.release()
        logging.info(f'{self.getName()} at {datetime.datetime.now()}')


def make_workers(workers, host, port):
    web_server = WebServer(host, port)
    for i in range(workers):
        t = ThreadClass(web_server)
        t.start()

    # allgo.acquire()
    # allgo.notify_all()
    # allgo.release()


if __name__ == "__main__":
    logging.basicConfig(
        filename='./logs.log',
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S')

    op = OptionParser()
    op.add_option('-p', '--port', action='store', default=8080)
    op.add_option('--host', '--host', action='store', default='127.0.0.1')
    op.add_option('-n', '--name', action='store', default='httpd')
    op.add_option('-w', '--workers', action='store', default=4)

    (opts, args) = op.parse_args()

    host = opts.host
    port = int(opts.port)
    name = opts.name
    workers = opts.workers

    make_workers(int(workers), host, port)
