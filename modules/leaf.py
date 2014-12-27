
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

  def get_positions(self):

    v = self.veins[:self.vnum,:]
    s = self.geometry.sources

    return v,s

  def get_distances(self,v_xyz,s_xyz):

    from scipy.spatial import distance
    cdist = distance.cdist

    dvs = cdist(v_xyz,s_xyz,'euclidean') # i x j
    dvv = cdist(v_xyz,v_xyz,'euclidean') # i x i

    return dvv,dvs

  def make_maps(self,dvv,dvs,killzone):

    from numpy import maximum, sum, reshape
    from collections import defaultdict

    vs_map = defaultdict(list)
    sv_map = {}

    nv,ns = dvs.shape

    for j in range(ns):

      near = set((dvs[:,j]<killzone).nonzero()[0])

      mas = maximum(dvv,dvs[:,j])
      compare = reshape(dvs[:,j],(nv,1))<mas
      mask = sum(compare,axis=1) == nv-1
      ii = mask.nonzero()[0]
      sv_map[j] = ii

      for i in [i for i in ii if i not in near]:
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

    get_closest_point = self.geometry.get_closest_point

    self.itt += 1

    stp = self.stp
    killzone = self.killzone
    noise = self.noise

    v_xyz,s_xyz = self.get_positions()
    dvv,dvs = self.get_distances(v_xyz,s_xyz)
    vs_map,sv_map = self.make_maps(dvv,dvs,killzone)

    nv,ns = dvs.shape

    for i,jj in vs_map.items():

      v = sum(s_xyz[jj,:]-v_xyz[i,:],axis=0)
      v = v/sqrt(sum(square(v)))

      ## im not sure how well this plane projection actually works
      d,pn = get_closest_point(v_xyz[i,:])
      vxpn = cross(v,pn)
      projected = cross(pn,vxpn)

      projected += random_unit_vector()*noise
      projected = projected/sqrt(sum(square(projected)))

      new = v_xyz[i,:] + projected*stp

      self.add_vein(i,new)

    ## mask out dead sources
    mask = ones(ns,'bool')
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

    ns = len(self.geometry.sources)
    nv = self.vnum
    itt = self.itt

    print('itt: {:d} sources: {:d} veins: {:d}'.format(itt,ns,nv))

    return

