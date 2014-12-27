#!/usr/bin/env python3



def main():

  from time import time

  from modules.geometry import Geometry
  from modules.leaf import Leaf

  steps = 1000
  noise = 0.1
  stp = 0.25
  killzone = stp*2.
  geom_fn = 'geom'
  leaf_fn = 'leaf'

  L = Leaf(stp,
           geometry = Geometry(geom_fn),
           noise = noise,
           killzone = killzone)

  t1 = time()

  for i in range(steps):
    L.grow()
    L.print_info()

    if len(L.geometry.sources)<1:
      break

  t2 = time()

  print('\n\ntime:', t2-t1)

  print('\n\nwriting leaf ...')
  L.to_file(leaf_fn)
  print('done.')

  return


if __name__ == '__main__':

  main()

