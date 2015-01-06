
def get_points_and_normals(geom):

  from numpy import row_stack

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

def get_random_even_indices(points,init_dist,init_num):

  from numpy import all, zeros, sqrt, square, sum
  from numpy.random import randint

  num = len(points)

  rnd_indices = randint(low=0,high=num,size=init_num)
  rnd_points = points[rnd_indices,:]

  mask = zeros(init_num,'bool')
  mask[0] = True

  for k in range(1,init_num):

    dx = rnd_points[k,:] - rnd_points[mask,:]
    dd = sqrt(sum(square(dx),axis=1))

    ok = all(dd>init_dist)
    if ok:
      mask[k] = True

  return rnd_indices[mask]

def get_seeds(seed):

  from numpy import row_stack

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

def mark_nodes(nodes):

  import bpy

  for x,y,z in nodes:
    bpy.ops.mesh.primitive_ico_sphere_add(
      subdivisions=1,
      size=0.2,
      location=(x,y,z))

  return

def save(fn):

  import bpy

  bpy.ops.wm.save_as_mainfile(filepath='./res/{:s}.blend'.format(fn))

  return


def main():

  import bpy

  out_fn = 'geom'
  source_fn = 'sources'

  geom_name = 'geom'
  seed_name = 'seed'

  init_num = 100
  stp = 0.25
  init_dist = stp*7.

  geom = bpy.data.objects[geom_name]
  points,normals = get_points_and_normals(geom)
  even_indices = get_random_even_indices(points,init_dist,init_num)

  sources = points[even_indices,:]
  source_normals = normals[even_indices,:]

  seed = bpy.data.objects[seed_name]
  seeds = get_seeds(seed)

  data = {
    'sources': sources,
    'source_normals': source_normals,
    'normals': normals,
    'points': points,
    'seeds': seeds
  }

  print('\n\nsources: {:d}'.format(len(sources)))
  print('source_normals: {:d}'.format(len(source_normals)))
  print('normals: {:d}'.format(len(normals)))
  print('points: {:d}'.format(len(points)))
  print('seeds: {:d}'.format(len(seeds)))

  print('\n\nwriting ...')
  mark_nodes(sources)
  save(source_fn)
  dump_to_file(data,out_fn)
  print('done.\n')


if __name__ == '__main__':

  main()

