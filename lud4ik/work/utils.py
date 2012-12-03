

def format_reply(reply):
    return bytes("{:4}{}".format(len(reply), reply), 'utf-8')