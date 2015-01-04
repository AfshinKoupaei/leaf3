
def random_unit_vector():

  from numpy.random import multivariate_normal
  from numpy import sqrt, sum, square, reshape

  x = multivariate_normal(mean=[0]*3,cov=[[1,0,0],[0,1,0],[0,0,1]],size=1)
  l = sqrt(sum(square(x)))

  return reshape(x/l,3)


class Leaf(object):

  def __init__(self,stp, geometry, noise, killzone):

    self.stp = stp
    self.geometry = geometry
    self.noise = noise
    self.killzone = killzone

    self.itt = 0

    self.nmax = 10**6
    self.__init_arrays()

    return

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

    for xyz in self.geometry.seeds:
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

  def get_triangulation(self,v):

    from scipy.spatial import Delaunay as delaunay

    flags = 'QJ Qc Pp'
    tri = delaunay(v,incremental=False,qhull_options=flags)

    return tri

  def get_positions(self):

    v = self.veins[:self.vnum,:]
    s = self.geometry.sources

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

  def simple_make_maps(self,v,s,dvs,killzone):

    from numpy import maximum, sum, reshape
    from collections import defaultdict
    from scipy.spatial import distance
    cdist = distance.cdist

    vs_map = defaultdict(list)
    sv_map = {}

    vnum,snum = dvs.shape

    dvv = cdist(v,v,'euclidean')

    for j in range(snum):

      near = set((dvs[:,j]<killzone).nonzero()[0])

      mas = maximum(dvv,dvs[:,j])
      compare = reshape(dvs[:,j],(vnum,1))<mas
      mask = sum(compare,axis=1) == vnum-1
      ii = mask.nonzero()[0]

      if len(ii)<1:
        continue

      sv_map[j] = ii

      for i in [i for i in ii if i not in near]:
        vs_map[i].append(j)

    return vs_map,sv_map

  def make_maps(self,v,s,dvs,killzone):

    from numpy import maximum, sum, reshape, column_stack, row_stack
    #from numpy import tensordot, logical_and
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

    #source_normals = self.geometry.source_normals
    #vein_normals = self.vein_normals
    neighbors = tri.neighbors

    simplex_vertex = tri.simplices
    js = tri.find_simplex(s,bruteforce=True,tol=1e-10)
    candidate_simplices = column_stack( (tri.neighbors[js],js) )

    vv = self.extended_neighborhood(neighbors,simplex_vertex,candidate_simplices)

    for j,ii in enumerate(vv):

      near = (dvs[ii,j]<killzone).nonzero()[0]

      #jn = source_normals[j,:]
      #vn = vein_normals[ii,:]
      #dots = tensordot(vn,jn,axes=1)
      #dotmask = dots>0.8

      iin = ii.shape[0]
      mas = maximum(cdist(v[ii,:],v[ii,:],'euclidean'),dvs[ii,j])
      compare = reshape(dvs[ii,j],(iin,1)) < mas
      mask = sum(compare,axis=1) == iin-1

      #mask = logical_and(mask,dotmask)

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

    _,_,normal = self.geometry.get_closest_point(new)
    self.vein_normals[vnum,:] = normal

    self.vnum += 1

    return vnum

  def grow(self):

    from numpy import sum, all, ones, dot, cross
    from scipy.spatial import distance
    from numpy.linalg import norm

    cdist = distance.cdist

    self.itt += 1

    geometry = self.geometry
    get_closest_point = geometry.get_closest_point

    stp = self.stp
    killzone = self.killzone

    vein_normals = self.vein_normals
    vnum = self.vnum
    snum = len(geometry.sources)

    v,s = self.get_positions()
    dvs = cdist(v,s,'euclidean')

    if vnum>100:
      vs_map,sv_map = self.make_maps(v,s,dvs,killzone)
    else:
      vs_map,sv_map = self.simple_make_maps(v,s,dvs,killzone)


    for i,jj in vs_map.items():

      vi = v[i,:]

      pn = vein_normals[i,:]

      sourcediff = s[jj,:]-vi
      direction = sum(sourcediff,axis=0)
      plane_direction = direction - dot(direction,pn) * pn
      plane_direction[:] /= norm(plane_direction)
      new = vi + plane_direction*stp

      #vec = sum(s[jj,:]-v[i,:],axis=0)
      #vec[:] /= norm(vec)

      #_,_,pn = get_closest_point(vi)
      #vxpn = cross(vec,pn)
      #projected = cross(pn,vxpn)

      ##projected += random_unit_vector()*noise
      #projected[:] /= norm(projected)
      #new = vi + projected*stp

      self.add_vein(i,new)

    ## mask out dead sources
    mask = ones(snum,'bool')
    for j,ii in sv_map.items():

      if all(dvs[ii,j]<=killzone):

        mask[j] = False

        print('merging:',len(ii),'deleted source:',j)

        if len(ii)>0:

          new = geometry.sources[j,:]
          new_num = self.add_vein(ii[0],new)
          self.merges[new_num].extend(ii)

    geometry.sources = geometry.sources[mask,:]
    geometry.source_normals = geometry.source_normals[mask,:]

    return

  def print_info(self):

    snum = len(self.geometry.sources)
    vnum = self.vnum
    itt = self.itt

    print('itt: {:d} sources: {:d} veins: {:d}'.format(itt,snum,vnum))

    return

