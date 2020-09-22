import http.server
import socketserver

PORT = 8050

def handler_from(directory):
    def _init(self, *args, **kwargs):
        return http.server.SimpleHTTPRequestHandler.__init__(self, *args, directory=self.directory, **kwargs)
    return type(f'HandlerFrom<{directory}>',
                (http.server.SimpleHTTPRequestHandler,),
                {'__init__': _init, 'directory': directory})

with socketserver.TCPServer(("", PORT), handler_from("output")) as httpd:
    print("serving at port", PORT)
    print("Close Server with CTRL-c")
    try: 
        httpd.serve_forever(); 
    except KeyboardInterrupt: 
        pass; 
    httpd.server_close()
    print(" Server closed")