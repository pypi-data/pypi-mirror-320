from relationalai.std import rel

def watch(*args):
  rel.__pyrel_debug_watch.add(*args)
