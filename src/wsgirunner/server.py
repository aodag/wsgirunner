from wsgiref.simple_server import make_server

def wsgiref_server_factory(global_conf, host, port, **settings):
    def runner(app):
        httpd = make_server(host, int(port), app)
        httpd.serve_forever()
    return runner
