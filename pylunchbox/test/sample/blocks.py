from pylunchbox.core.modeling import MeshComponent
from pylunchbox.core.maths import Transformation, Vector2f

RIGHT = 0
TOP = 1

class _Block(object):

    def __init__(self, entity, mesh_comp, trans_comp):

        self.entity = entity
        self.bundle = mesh_comp
        self.trans = trans_comp

class BlockGenerator(object):

    def __init__(self, app, mesh):

        self._app = app
        self._mesh = mesh
        self._em = app.world.em
        self._cm = app.world.cm
    
    def create_block(self):

        block = self._em.create()
        trans_comp = self._cm.create(block.get_id(), Transformation)
        mesh_comp = self._cm.create(block.get_id(), MeshComponent)
        mesh = self._mesh.clone()
        mesh_comp.bundle = mesh

        return _Block(block, mesh_comp, trans_comp)

    def load_block(self, block):

        self._app.world.batch.add(block.entity)

    def set_face_texture(self, block, face, atlas, x, y):

        #uvs = atlas.get_uv_for(x, y)
        #for item in zip(block.bundle.bundle['cube'].uvs[:6], uvs):
        #    print item
        #block.bundle.bundle['cube'].uvs[:6] = uvs

        offset = Vector2f(x*0.0625, y*0.0625)
        temp = []
        for v in block.bundle.bundle['cube'].uvs[face*6:(face+1)*6]:
            v1 = v * 0.0625
            temp.append(v1 + offset)
            print v, v1 + offset
        block.bundle.bundle['cube'].uvs[face*6:(face+1)*6] = temp




    