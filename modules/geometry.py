
class Geometry(object):

  def __init__(self,fn):
    from scipy.spatial import cKDTree

    data = self.__load_from_file(fn)

    self.sources = data['sources']
    self.source_normals = data['source_normals']
    self.normals = data['normals']
    self.points = data['points']
    self.seeds = data['seeds']
    self.tree = cKDTree(self.points)
    self.query = self.tree.query

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

  def get_closest_point(self,x):

    d,i = self.query(x,1)
    normal = self.normals[i,:]
    p = self.points[i,:]

    return p,d,normal

