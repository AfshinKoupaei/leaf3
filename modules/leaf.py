
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

    vnum = 0
    bnum = 0

    nmax = self.nmax
    self.parent = zeros(nmax,'int')-1
    self.first_descendant = zeros(nmax,'int')-1
    self.radius = zeros(nmax,'int')
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
      'merges': self.merges,
      'first_descendant': self.first_descendant[:vnum]
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

  def grow(self):

    from numpy import sum, all, ones, square, sqrt, cross

    get_closest_point = self.geometry.get_closest_point

    self.itt += 1

    vnum = self.vnum

    stp = self.stp
    killzone = self.killzone
    #noise = self.noise

    veins = self.veins
    parent = self.parent
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

      #projected += random_unit_vector()*noise
      projected = projected/sqrt(sum(square(projected)))

      new = v_xyz[i,:] + projected*stp
      veins[vnum,:] = new
      parent[vnum] = i
      vnum += 1

    ## mask out dead sources
    mask = ones(ns,'bool')
    for j,ii in sv_map.items():

      if all(dvs[ii,j]<=killzone):

        mask[j] = False

        print('merging:',len(ii),'deleted source:',j)

        self.merges.append(ii)
        for i in ii:
          veins[vnum,:] = self.geometry.sources[j,:]

    self.geometry.sources = self.geometry.sources[mask,:]
    self.vnum = vnum

    return

  def print_info(self):

    ns = len(self.geometry.sources)
    nv = self.vnum
    itt = self.itt

    print('itt: {:d} sources: {:d} veins: {:d}'.format(itt,ns,nv))

    return

