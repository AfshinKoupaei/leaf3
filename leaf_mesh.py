import bpy
import bmesh


class LeafMesh(object):

  def __init__(self,in_fn):

    obj_name = 'leaf'

    mesh = bpy.data.meshes.new('leafSkin')
    obj = bpy.data.objects.new(obj_name, mesh)

    scn = bpy.context.scene
    scn.objects.link(obj)
    scn.objects.active = obj
    obj.select = True

    self.obj_name = obj_name
    self.obj = obj

    self.data = self.__load_from_file(in_fn)

    return

  def save(self,fn):

    bpy.ops.wm.save_as_mainfile(filepath=fn)

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

  def __get_bmesh(self):

    bpy.data.objects[self.obj_name].select = True
    self.obj = bpy.context.active_object
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(self.obj.data)

    return bm

  def __to_mesh(self):

    bpy.ops.object.mode_set(mode='OBJECT')

    return

  def get_branches(self):

    from operator import itemgetter

    descendants = self.data['descendants']
    parent = self.data['parent']
    queue = [0]
    radius = self.radius

    branches = []

    while queue:

      b = queue.pop()
      branch = [b]

      while True:

        des = descendants[b]

        if len(des)<1:
          break

        dw = zip(des,radius[des])
        dw = sorted(dw,key=itemgetter(1))
        first = dw.pop()[0]

        queue.extend([d for d,_ in dw])
        b = first

        branch.append(b)

      branches.append(branch)

    self.branches = branches

    return

  def make_skeleton(self):

    bm = self.__get_bmesh()
    verts = bm.verts
    veins = self.data['veins']
    parent = self.data['parent']
    merges = self.data['merges']

    for vert in veins:
      verts.new(vert)

    for i,p in enumerate(parent):
      if i<0 or p<0:
        continue
      bm.edges.new([verts[i],verts[p]])

    for j,mm in merges.items():

      for m in mm:
        try:
          bm.edges.new([verts[j],verts[m]])
        except ValueError:
          pass

    self.__to_mesh()

    return


  def set_radius(self,min_rad):

    from numpy import zeros, sqrt, max

    parent = self.data['parent']
    vnum = parent.shape[0]

    radius = zeros(vnum,'int')

    for i in reversed(range(vnum)):

      k = parent[i]

      while k > 0:

        radius[k] += 1.
        k = parent[k]

    wmax = max(radius)
    radius = sqrt(sqrt(radius/wmax))
    radius[radius<min_rad] = min_rad

    self.radius = radius

  def skin(self,rad_scale):

    obj_name = self.obj_name

    bpy.context.scene.objects.active = bpy.data.objects[obj_name]
    bpy.data.objects[obj_name].select = True
    bpy.ops.object.modifier_add(type='SKIN')
    bpy.ops.object.mode_set(mode='OBJECT')

    mod_skin = bpy.data.objects[obj_name].modifiers['Skin']
    mod_skin.use_x_symmetry = False
    mod_skin.use_y_symmetry = False
    mod_skin.use_z_symmetry = False

    skin_vertices = self.obj.data.skin_vertices[0].data

    radius = self.radius

    for i,v in enumerate(skin_vertices):

      v.radius[:] = [radius[i]*rad_scale]*2
      v.use_loose = True
      v.use_root = False

    skin_vertices[0].use_root = True

    bpy.ops.object.modifier_apply(apply_as='DATA',modifier="Skin")

    #bm = self.__get_bmesh()
    #bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.001)
    #self.__to_mesh()

    bpy.data.objects[obj_name].select = True
    bpy.ops.object.modifier_add(type='TRIANGULATE')
    bpy.ops.object.modifier_add(type='SMOOTH')

    return


def main():

  from time import time

  t1 = time()

  in_fn = 'leaf'
  out_fn = 'res'

  min_rad = 0.2
  rad_scale = 2.

  LM = LeafMesh(in_fn)

  print('setting radius ...\n')
  LM.set_radius(min_rad)
  print('done.\n')

  print('making skeleton ...\n')
  LM.make_skeleton()
  print('done.\n')

  LM.save('./res/{:s}_skel.blend'.format(out_fn))

  print('applying skin ...\n')
  LM.skin(rad_scale)
  print('done.\n')

  LM.save('./res/{:s}.blend'.format(out_fn))

  print('\ntime:',time()-t1,'\n\n')

  return


if __name__ == '__main__':

  main()

