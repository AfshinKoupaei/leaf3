#!/usr/bin/env python3

def main():

  from time import time

  from src.leaf import Leaf

  steps = 1000
  noise = 0
  geom_fn = 'geom'
  leaf_fn = 'leaf'

  simple_map_limit = 10

  source_count_terminate = 1

  force_plane_projection = False
  normal_compare = False
  normal_limit = 0.6

  L = Leaf(geom_fn,noise = noise)

  t1 = time()

  for i in range(steps):
    try:
      L.grow(simple_map_limit=simple_map_limit,
             force_plane_projection=force_plane_projection,
             normal_compare=normal_compare,
             normal_limit=normal_limit)
      L.print_info()

      if len(L.sources)<source_count_terminate:
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

