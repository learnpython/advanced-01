def make_message(command, data=''):
    body = '\n'.join([command, data])
    return ('%4d%s' % (len(body), body)).encode('utf-8')
