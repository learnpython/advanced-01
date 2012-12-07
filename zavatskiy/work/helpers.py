def make_message(command, data=''):
    body = '\n'.join([command, data])
    return ('%4d%s' % (len(body), body)).encode('utf-8')

def parse_message(recv):
    buf_size = recv(4).decode('utf-8').strip()
    if not buf_size:
        return None
    buf = recv(int(buf_size)).decode('utf-8')
    return buf.split('\n', 1)

