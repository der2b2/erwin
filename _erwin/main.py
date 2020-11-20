from _erwin import build
from _erwin import serve
from _erwin import clean
from _erwin import initialize

def run(argv):
    if argv[1] == "clean" or argv[1] == "c":
      print("Clean")
      clean.run_clean()
    elif argv[1] == "build" or argv[1] == "b":
      print("Build")
      build.main()
    elif argv[1] == "serve" or argv[1] == "s":
      print("Serve")
      serve.run_server()
    elif argv[1] == "init" or argv[1] == "i":
      print("Initialize")
      print("")
      read = input("Initialize will override templates, sure you want to proceed? [Y|n] ")
      if read == "Y":
        initialize.run_init()
      else:
        print("Aborted")
    else:
      print("usage: python erwin.py build|serve|clean|init b|s|c|i")
 
