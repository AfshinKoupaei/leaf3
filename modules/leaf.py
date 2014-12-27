
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

    self.merges = []

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
      sv_map[j] = ii

      for i in [i for i in ii if i not in near]:
        vs_map[i].append(j)

    return vs_map,sv_map

  def make_maps(self,v,s,dvs,killzone):

    from numpy import maximum, sum, reshape, column_stack,\
      unique, row_stack, concatenate
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

    def valid(x):
      x = x[x<vnum]
      x = x[x>-1]
      return x

    def positive(x):
      x = x[x>-1]
      return x

    tri = self.get_triangulation(stacked)
    neighbors = tri.neighbors

    # simplex -> vertices
    p  = tri.simplices
    # s -> simplex
    js = tri.find_simplex(s,bruteforce=True,tol=1e-10)
    # s -> neighboring simplices including s
    neigh = column_stack( (tri.neighbors[js],js) )
    # s -> potential neighboring points

    vv = []
    for ns in neigh:
      cand_neigh = positive(ns)
      num_neigh = len(cand_neigh)
      neigh_neigh = reshape(neighbors[cand_neigh,:],num_neigh*4)
      all_neigh = concatenate((cand_neigh,neigh_neigh))
      valid_neigh = unique(positive(all_neigh))
      vv.append(unique(valid(p[valid_neigh,:])))

    for j,ii in enumerate(vv):

      near = set((dvs[ii,j]<killzone).nonzero()[0])

      iin = ii.shape[0]
      mas = maximum(cdist(v[ii,:],v[ii,:],'euclidean'),dvs[ii,j])

      ## ||v-s|| < mas
      compare = reshape(dvs[ii,j],(iin,1)) < mas
      mask = sum(compare,axis=1) == iin-1

      sv_map[j] = ii[mask]

      ## TODO: deadlock fix
      #for i in ii[mask]:
        #vs_map[i].append(j)

      near_i = [i for i in ii[mask] if i not in ii[list(near)]]
      #print(ii,ii[mask],near,near_i)
      for i in near_i:
        vs_map[i].append(j)

    return vs_map,sv_map

  def add_vein(self,i,new):

    vnum = self.vnum

    self.veins[vnum,:] = new
    self.parent[vnum] = i

    self.generation[vnum] = self.generation[i] if \
                              len(self.descendants[i])<1 else\
                              self.generation[i]+1
    self.descendants[i].append(vnum)

    self.vnum += 1

    return

  def grow(self):

    from numpy import sum, all, ones, square, sqrt, cross
    from scipy.spatial import distance
    cdist = distance.cdist

    self.itt += 1

    get_closest_point = self.geometry.get_closest_point
    stp = self.stp
    killzone = self.killzone
    noise = self.noise

    vnum = self.vnum
    snum = len(self.geometry.sources)

    v,s = self.get_positions()
    dvs = cdist(v,s,'euclidean') # i x j

    if vnum>100:
      vs_map,sv_map = self.make_maps(v,s,dvs,killzone)
    else:
      vs_map,sv_map = self.simple_make_maps(v,s,dvs,killzone)


    for i,jj in vs_map.items():

      vec = sum(s[jj,:]-v[i,:],axis=0)
      vec = vec/sqrt(sum(square(vec)))

      ## im not sure how well this plane projection actually works
      d,pn = get_closest_point(v[i,:])
      vxpn = cross(vec,pn)
      projected = cross(pn,vxpn)

      projected += random_unit_vector()*noise
      projected = projected/sqrt(sum(square(projected)))

      new = v[i,:] + projected*stp

      self.add_vein(i,new)

    ## mask out dead sources
    mask = ones(snum,'bool')
    for j,ii in sv_map.items():

      if all(dvs[ii,j]<=killzone):

        mask[j] = False

        print('merging:',len(ii),'deleted source:',j)

        self.merges.append(ii)
        for i in ii:

          new = self.geometry.sources[j,:]
          self.add_vein(i,new)

    self.geometry.sources = self.geometry.sources[mask,:]

    return

  def print_info(self):

    snum = len(self.geometry.sources)
    vnum = self.vnum
    itt = self.itt

    print('itt: {:d} sources: {:d} veins: {:d}'.format(itt,snum,vnum))

    return

