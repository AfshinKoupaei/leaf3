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

  def make_skeleton(self):

    bm = self.__get_bmesh()
    verts = bm.verts
    veins = self.data['veins']
    parent = self.data['parent']

    for vert in veins:
      verts.new(vert)

    for i,p in enumerate(parent):
      if i<0 or p<0:
        continue
      bm.edges.new([verts[i],verts[p]])

    self.__to_mesh()

    return

  def save(self,fn):

    bpy.ops.wm.save_as_mainfile(filepath=fn)

    return

  def skin(self):

    bpy.context.scene.objects.active = bpy.data.objects[self.obj_name]
    bpy.data.objects[self.obj_name].select = True
    bpy.ops.object.modifier_add(type='SKIN')

    bpy.ops.object.mode_set(mode='OBJECT')

    n = float(len(self.obj.data.vertices))
    for i,v in enumerate(self.obj.data.skin_vertices[0].data):
      rad = 1.-float(i)/n
      v.radius[:] = [0.25*rad]*2

    return


def main():

  in_fn = 'leaf'
  out_fn = 'res'

  LM = LeafMesh(in_fn)

  LM.make_skeleton()

  LM.skin()

  LM.save('./res/{:s}.blend'.format(out_fn))

  return


if __name__ == '__main__':

  main()

