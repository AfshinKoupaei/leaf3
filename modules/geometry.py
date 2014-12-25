
class Geometry(object):

  def __init__(self,fn):
    from scipy.spatial import cKDTree

    data = self.__load_from_file(fn)

    self.sources = data['sources']
    self.normals = data['normals']
    self.centers = data['centers']
    self.seeds = data['seeds']
    self.tree = cKDTree(self.centers)
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

    return d,normal

