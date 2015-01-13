
class Leaf(object):

  def __init__(self,geom_fn,noise) :

    from scipy.spatial import cKDTree

    self.noise = noise

    self.itt = 0

    self.nmax = 10**6

    data = self.__load_from_file(geom_fn)

    self.sources = data['sources']
    self.source_normals = data['source_normals']
    self.normals = data['normals']
    self.points = data['points']
    self.seeds = data['seeds']
    self.stp = data['stp']
    self.killzone = data['killzone']
    self.tree = cKDTree(self.points)
    self.query = self.tree.query

    self.__init_arrays()

    return

  def __load_from_file(self,fn):

    try:
      import cPickle as pickle
    except:
      import pickle

    f = open('./res/{:s}.pkl'.format(fn), 'rb')
    try:
      data = pickle.loads(pickle.load(f))
    finally:
      f.close()

    return data

  def __init_arrays(self):

    from numpy import zeros
    from collections import defaultdict

    vnum = 0
    bnum = 0

    nmax = self.nmax
    self.parent = zeros(nmax,'int')-1
    self.descendants = defaultdict(list)
    self.generation = zeros(nmax,'int')
    self.veins = zeros((nmax,3),'float')
    self.vein_normals = zeros((nmax,3),'float')

    self.merges = defaultdict(list)

    for xyz in self.seeds:
      self.veins[vnum,:] = xyz
      vnum += 1

    self.vnum = vnum
    self.bnum = bnum

    return

  def to_file(self,fn):

    try:
      import cPickle as pickle
    except:
      import pickle

    vnum = self.vnum

    data = {
      'veins': self.veins[:vnum,:],
      'parent': self.parent[:vnum],
      'generation': self.generation[:vnum],
      'merges': self.merges,
      'descendants': self.descendants
    }

    out = open('./res/{:s}.pkl'.format(fn), 'wb')
    try:
      pickle.dump(pickle.dumps(data),out)
    finally:
      out.close()

    return

  def get_closest_point(self,x):

    d,i = self.query(x,1)
    normal = self.normals[i,:]
    p = self.points[i,:]

    return p,d,normal

  def get_triangulation(self,v):

    from scipy.spatial import Delaunay as delaunay

    flags = 'QJ Qc Pp'
    tri = delaunay(v,incremental=False,qhull_options=flags)

    return tri

  def get_positions(self):

    v = self.veins[:self.vnum,:]
    s = self.sources

    return v,s

  def extended_neighborhood(self,neighbors,simplex_vertex,candidate_simplices):

    from numpy import unique, concatenate, reshape

    vnum = self.vnum

    def valid(x):
      x = unique(x)
      x = x[x<vnum]
      x = x[x>-1]
      return x

    def positive(x):
      x = x[x>-1]
      return x

    vv = []
    for simp in candidate_simplices:

      simp1 = positive(simp)
      simp2 = positive(neighbors[simp1,:].flatten())
      simp3 = positive(neighbors[simp2,:].flatten())
      simp4 = positive(neighbors[simp3,:].flatten())
      all_simp = unique(concatenate((simp,simp2,simp3,simp4)))

      vv.append(valid(simplex_vertex[all_simp,:].flatten()))

    return vv

  def simple_make_maps(self,v,s,dvs,killzone,normal_compare,normal_limit):

    from numpy import maximum, sum, reshape
    from numpy import tensordot, logical_and
    from collections import defaultdict
    from scipy.spatial import distance
    cdist = distance.cdist

    vs_map = defaultdict(list)
    sv_map = {}

    vnum,snum = dvs.shape
    source_normals = self.source_normals
    vein_normals = self.vein_normals

    dvv = cdist(v,v,'euclidean')

    for j in range(snum):

      near = set((dvs[:,j]<killzone).nonzero()[0])

      mas = maximum(dvv,dvs[:,j])
      compare = reshape(dvs[:,j],(vnum,1))<mas
      mask = sum(compare,axis=1) == vnum-1

      # TODO: implement this as well?
      #if normal_compare:

        #jn = source_normals[j,:]
        #vn = vein_normals[:,:]
        #dots = tensordot(vn,jn,axes=1)
        #dotmask = dots>normal_limit
        #mask = logical_and(mask,dotmask)

      ii = mask.nonzero()[0]

      if len(ii)<1:
        continue

      sv_map[j] = ii

      for i in [i for i in ii if i not in near]:
        vs_map[i].append(j)

    return vs_map,sv_map

  def make_maps(self,v,s,dvs,killzone,normal_compare,normal_limit):

    from numpy import maximum, sum, reshape, column_stack, row_stack
    from numpy import tensordot, logical_and
    from collections import defaultdict
    from scipy.spatial import distance
    cdist = distance.cdist

    vnum,snum = dvs.shape

    vs_map = defaultdict(list)
    sv_map = {}

    stacked = row_stack((
      v,
      [[-1000,-1000,-1000],
      [1000,-1000,-1000],
      [-1000,1000,-1000],
      [1000,1000,-1000],
      [-1000,-1000,1000],
      [1000,-1000,1000],
      [-1000,1000,1000],
      [1000,1000,1000]]
    ))

    tri = self.get_triangulation(stacked)

    source_normals = self.source_normals
    vein_normals = self.vein_normals
    neighbors = tri.neighbors

    simplex_vertex = tri.simplices
    js = tri.find_simplex(s,bruteforce=True,tol=1e-10)
    candidate_simplices = column_stack( (tri.neighbors[js],js) )

    vv = self.extended_neighborhood(neighbors,simplex_vertex,candidate_simplices)

    for j,ii in enumerate(vv):

      near = (dvs[ii,j]<killzone).nonzero()[0]

      iin = ii.shape[0]
      mas = maximum(cdist(v[ii,:],v[ii,:],'euclidean'),dvs[ii,j])
      compare = reshape(dvs[ii,j],(iin,1)) < mas
      mask = sum(compare,axis=1) == iin-1

      if normal_compare:

        jn = source_normals[j,:]
        vn = vein_normals[ii,:]
        dots = tensordot(vn,jn,axes=1)
        dotmask = dots>normal_limit
        mask = logical_and(mask,dotmask)

      if len(ii[mask])<1:
        continue

      sv_map[j] = ii[mask]

      near_i = ( i for i in ii[mask] if i not in ii[near])
      for i in near_i:
        vs_map[i].append(j)

    return vs_map,sv_map

  def add_vein(self,parent,new):

    vnum = self.vnum

    self.veins[vnum,:] = new
    self.parent[vnum] = parent

    if len(self.descendants[parent])<1:
      gen = self.generation[parent]
    else:
      gen = self.generation[parent]+1

    self.generation[vnum] = gen
    self.descendants[parent].append(vnum)

    _,_,normal = self.get_closest_point(new)
    self.vein_normals[vnum,:] = normal

    self.vnum += 1

    return vnum

  def grow(self,
           simple_map_limit,
           force_plane_projection=True,
           normal_compare=False,
           normal_limit=0.5):

    from numpy import sum, all, ones, dot
    from scipy.spatial import distance
    from numpy.linalg import norm

    cdist = distance.cdist

    self.itt += 1

    stp = self.stp
    killzone = self.killzone

    sources = self.sources
    source_normals = self.source_normals

    vein_normals = self.vein_normals
    vnum = self.vnum
    snum = len(sources)

    v,s = self.get_positions()
    dvs = cdist(v,s,'euclidean')

    if vnum>simple_map_limit:
      vs_map,sv_map = self.make_maps(v,s,dvs,killzone,
                                     normal_compare,
                                     normal_limit)
    else:
      vs_map,sv_map = self.simple_make_maps(v,s,dvs,killzone,
                                            normal_compare,
                                            normal_limit)


    for i,jj in vs_map.items():

      vi = v[i,:]

      pn = vein_normals[i,:]

      sourcediff = s[jj,:]-vi
      direction = sum(sourcediff,axis=0)
      if force_plane_projection:
        plane_direction = direction - dot(direction,pn) * pn
        plane_direction[:] /= norm(plane_direction)
        new = vi + plane_direction*stp
      else:
        new = vi + direction/norm(direction)*stp

      self.add_vein(i,new)

    ## mask out dead sources
    mask = ones(snum,'bool')
    for j,ii in sv_map.items():

      if all(dvs[ii,j]<=killzone):

        mask[j] = False

        print('merging:',len(ii),'deleted source:',j)

        if len(ii)>0:

          new = sources[j,:]
          new_num = self.add_vein(ii[0],new)
          self.merges[new_num].extend(ii)

    self.sources = sources[mask,:]
    self.source_normals = source_normals[mask,:]

    return

  def print_info(self):

    snum = len(self.sources)
    vnum = self.vnum
    itt = self.itt

    print('itt: {:d} sources: {:d} veins: {:d}'.format(itt,snum,vnum))

    return

