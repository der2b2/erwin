import http.server
import socketserver
import os
import configparser

def handler_from(directory):
    def _init(self, *args, **kwargs):
        print(self.directory)
        return http.server.SimpleHTTPRequestHandler.__init__(self, *args, directory=self.directory, **kwargs)
    return type(f'HandlerFrom<{directory}>',
                (http.server.SimpleHTTPRequestHandler,),
                {'__init__': _init, 'directory': directory})

def run_server():      
    #initiate configs
    config = configparser.ConfigParser()
    config.read('site_config.ini')
    port = int(config['DEFAULT']['Webserver Port'])   
    print(os.getcwd())
    os.chdir("output")                
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        print("serving at port", port)
        print("Close Server with CTRL-c")
        try: 
            httpd.serve_forever(); 
        except KeyboardInterrupt: 
            pass; 
        httpd.server_close()
        print(" Server closed")
