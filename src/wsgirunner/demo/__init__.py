def app(environ, start_response):
    start_response("200 OK",
        [('Content-type', 'text/plain')])
    return [b'Hello, world!', b"good-bye!"]

def main(global_conf, **settings):
    return app
