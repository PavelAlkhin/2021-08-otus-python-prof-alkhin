import socket
import sys
import threading

allgo = threading.Condition()


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
    request_data = request.decode()
    data = parse_request_line(request_data)

    print('Received {}'.format(request))
    list_path = data['resource'].split('/')
    path = ''
    for p in list_path:
        if p == '':
            path += "/"
            continue
        if p == '/':
            path += p
            continue
        if '.' in p:
            path += p
        else:
            path += f'{p}/'

    if '.' not in path:
        path += 'index.html'
    index_file = f'.{path}'
    try:
        with open(index_file, 'rb') as f:  # open file , r => read , b => byte format
            response = f.read()

        header = 'HTTP/1.1 200 OK\n'

        if (index_file.endswith(".jpg")):
            mimetype = 'image/jpg'
        elif (index_file.endswith(".css")):
            mimetype = 'text/css'
        else:
            mimetype = 'text/html'

        header += 'Content-Type: ' + str(mimetype) + '\n\n'

    except Exception as e:
        header = 'HTTP/1.1 404 Not Found\n\n'
        response = '<html><body><center><h3>Error 404: Resourse not found</h3><p>Python HTTP Server</p></center></body></html>'.encode(
            'utf-8')

    final_response = header.encode('utf-8')
    final_response += response
    client_socket.send(final_response)
    client_socket.close()


class ThreadClass(threading.Thread):

    def __init__(self, web_server):
        self.server = web_server
        super().__init__()

    def run(self):
        print('Listening on {}:{}'.format(self.server.bind_ip, self.server.bind_port))

        while True:
            client_sock, address = self.server.server.accept()
            print('Accepted connection from {}:{}'.format(address[0], address[1]))
            client_handler = threading.Thread(
                target=handle_client_connection,
                args=(client_sock,)
            )
            client_handler.start()
        serv_sock.close()

        allgo.acquire()
        allgo.wait()
        allgo.release()
        print("%s at %s\n" % (self.getName(), datetime.datetime.now()))


def main(c_workers, web_server):
    for i in range(c_workers):
        t = ThreadClass(web_server)
        t.start()

    allgo.acquire()
    allgo.notify_all()
    allgo.release()


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    name = sys.argv[3]
    args = sys.argv
    count_args = len(args)
    c_workers = 1
    for i in range(1, count_args):
        if sys.argv[i] == '-w':
            c_workers = int(sys.argv[i + 1])
            break
    web_server = WebServer(host, port)
    main(c_workers, web_server)
