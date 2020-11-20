from _erwin import build
from _erwin import serve
from _erwin import clean
from _erwin import initialize

def run(argv):
    if argv[0] == "clean" or argv[0] == "c":
      print("Cleaning output folder")
      clean.run_clean()
    elif argv[0] == "build" or argv[0] == "b":
      print("Build")
      build.main()
    elif argv[0] == "serve" or argv[0] == "s":
      print("Serve")
      serve.run_server()
    elif argv[0] == "init" or argv[0] == "i":
      print("Initialize")
      print("")
      read = input("Initialize will override templates, sure you want to proceed? [Y|n] ")
      if read == "Y":
        initialize.run_init()
      else:
        print("Aborted")
    else:
      print("usage: python erwin.py build|serve|clean|init b|s|c|i")
 
