#!/usr/bin/env python3

def main():

  from time import time

  from src.geometry import Geometry
  from src.leaf import Leaf

  steps = 500
  noise = 0.1
  stp = 0.25
  killzone = stp*2.
  geom_fn = 'geom'

  G = Geometry(geom_fn)

  L = Leaf(stp,
           geometry = G,
           noise = noise,
           killzone = killzone)

  t1 = time()

  for i in range(steps):
    L.grow()
    L.print_info()

    if len(L.geometry.sources)<1:
      break

  t2 = time()

  print('time:', t2-t1)

  return


if __name__ == '__main__':

  main()

