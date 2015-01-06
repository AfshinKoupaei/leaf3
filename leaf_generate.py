#!/usr/bin/env python3

def main():

  from time import time

  from modules.geometry import Geometry
  from modules.leaf import Leaf

  steps = 1000
  noise = 0
  stp = 0.25
  killzone = stp*2.
  geom_fn = 'geom'
  leaf_fn = 'leaf'

  simple_map_limit = 10

  source_count_terminate = 1
  normal_compare = True
  normal_limit = 0.5

  L = Leaf(stp,
           geometry = Geometry(geom_fn),
           noise = noise,
           killzone = killzone)

  t1 = time()

  for i in range(steps):
    try:
      L.grow(simple_map_limit = simple_map_limit,
             normal_compare=normal_compare,
             normal_limit=normal_limit)
      L.print_info()

      if len(L.geometry.sources)<source_count_terminate:
        break
    except KeyboardInterrupt:
      print('KeyboardInterrupt')
      break

  t2 = time()

  print('\n\ntime:', t2-t1)

  print('\n\nwriting leaf ...')
  L.to_file(leaf_fn)
  print('done.')

  return


if __name__ == '__main__':

  main()

