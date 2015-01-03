
def get_random_even_points(geom_name,init_dist,init_num):

  import bpy
  from numpy import row_stack, all, zeros, sqrt, square, sum
  from numpy.random import randint

  geom = bpy.data.objects[geom_name]
  mat = geom.matrix_world
  polys = geom.data.polygons
  num = len(polys)

  source_vectors = []

  for i in range(init_num):
    k = randint(0,num)
    loc = polys[k]
    glob = mat*loc.center
    source_vectors.append(glob)

  sources = row_stack(source_vectors)

  mask = zeros(init_num,'bool')
  mask[0] = True

  for i in range(1,init_num):

    dx = sources[i,:] - sources[mask,:]
    dd = sqrt(sum(square(dx),axis=1))

    ok = all(dd>init_dist)
    if ok:
      mask[i] = True

  sources = sources[mask,:]

  return sources


def get_points_and_normals(geom_name):

  import bpy
  from numpy import row_stack

  geom = bpy.data.objects[geom_name]
  mat = geom.matrix_world

  normals = []
  points = []
  for f in geom.data.polygons:
    normals.append(f.normal)
    points.append(mat*f.center)

  for v in geom.data.vertices:
    normals.append(v.normal)
    points.append(mat*v.co)

  return row_stack(points),row_stack(normals)


def get_seeds(seed_name):

  import bpy
  from numpy import row_stack

  seed = bpy.data.objects[seed_name]
  mat = seed.matrix_world
  seeds = []
  for v in seed.data.vertices:
    glob = mat*v.co
    seeds.append(glob)

  return row_stack(seeds)


def dump_to_file(data,fn):

  try:
    import cPickle as pickle
  except:
    import pickle

  out = open('./res/{:s}.pkl'.format(fn), 'wb')
  try:
    pickle.dump(pickle.dumps(data),out)
  finally:
    out.close()


def main():

  geom_name = 'geom'
  seed_name = 'seed'

  out_fn = 'geom'

  sinit = 50
  stp = 0.20
  init_dist = stp*4

  sources = get_random_even_points(geom_name,init_dist,sinit)
  points,normals = get_points_and_normals(geom_name)
  seeds = get_seeds(seed_name)

  data = {
    'sources': sources,
    'normals': normals,
    'points': points,
    'seeds': seeds
  }

  print('\n\nsources: {:d}'.format(len(sources)))
  print('points: {:d}'.format(len(points)))
  print('normals: {:d}'.format(len(normals)))
  print('seeds: {:d}'.format(len(seeds)))

  print('\n\nwriting ...')
  dump_to_file(data,out_fn)
  print('done.\n')


if __name__ == '__main__':

  main()

