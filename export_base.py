
def get_random_even_points(geom_name,init_dist,init_num):

  import bpy
  from numpy import row_stack, all, zeros
  from numpy.random import randint
  from scipy.spatial import distance
  cdist = distance.cdist

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
  dss = cdist(sources,sources,'euclidean')
  mask = zeros(init_num,'bool')
  for i in range(init_num-1):
    d = dss[i,i+1:]>init_dist
    ok = all(d)
    if ok:
      mask[i] = True

  sources = sources[mask,:]

  return sources


def get_centers_and_normals(geom_name):

  import bpy
  from numpy import row_stack

  geom = bpy.data.objects[geom_name]
  mat = geom.matrix_world

  normals = []
  centers = []
  for f in geom.data.polygons:
    normals.append(f.normal)
    glob = mat*f.center
    centers.append(glob)

  return row_stack(centers),row_stack(normals)


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

  sinit = 100
  stp = 0.25
  init_dist = stp*4

  sources = get_random_even_points(geom_name,init_dist,sinit)
  centers,normals = get_centers_and_normals(geom_name)
  seeds = get_seeds(seed_name)

  data = {
    'sources': sources,
    'normals': normals,
    'centers': centers,
    'seeds': seeds
  }

  print('\n\nsources: {:d}'.format(len(sources)))
  print('centers: {:d}'.format(len(centers)))
  print('normals: {:d}'.format(len(normals)))
  print('seeds: {:d}'.format(len(seeds)))

  print('\n\nwriting ...')
  dump_to_file(data,out_fn)
  print('done.\n')


if __name__ == '__main__':

  main()

