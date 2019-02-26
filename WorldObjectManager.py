from .WorldObject import WorldObject

class WorldObjectManager(object):
    def __init__(self):
        self.objects = {}
        self.objs_to_remove = set()

        self.object_links = {}

        self.objects_id = None
        self.next_obj_id = 1
        self.wm_dirty = False

    def get_object(self, handle):
        return self.objects.get(handle, None)

    def get_objects(self):
        return self.objects.values()

    def get_perception_id(self, handle):
        if handle in self.objects:
            return self.objects[handle].get_perception_id()
        return None

    def get_soar_handle(self, perc_id):
        return self.object_links.get(perc_id, None)

    def link_objects(self, src_handle, dest_handle):
        self.object_links[src_handle] = dest_handle
        if src_handle in self.objects:
            wobj = self.objects[src_handle]
            self.objs_to_remove.append(wobj)
            del self.objects[src_handle]
            if dest_handle not in self.objects:
                self.objects[dest_handle] = wobj.copy(dest_handle)
        self.wm_dirty = True

    def update(self, world_data):
        new_obj_data = {}

        for obj_data in world_data["objects"]:
            perc_id = str(obj_data["objectId"])
            handle = self.object_links.get(perc_id, None)
            if handle == None:
                handle = perc_id.split("|")[0] + str(self.next_obj_id)
                self.next_obj_id += 1
                self.object_links[perc_id] = handle
            new_obj_data[handle] = obj_data

        stale_objs = set(self.objects.keys())
        
        # For each object, either update existing or create if new
        for handle, obj_data in new_obj_data.items():
            if handle in self.objects:
                wobj = self.objects[handle]
                wobj.update(obj_data)
                stale_objs.remove(handle)
            else:
                self.objects[handle] = WorldObject(handle, obj_data)

        # Don't remove an object currently being held
        if len(world_data["inventoryObjects"]) > 0:
            perc_id = world_data["inventoryObjects"][0]["objectId"]
            handle = self.get_soar_handle(perc_id)
            if handle in stale_objs:
                stale_objs.remove(handle)

        # Remove all stale objects from WM
        for handle in stale_objs:
            self.objs_to_remove.add(self.objects[handle])
            del self.objects[handle]

        # Update object containing information
        for obj in self.objects.values():
            obj_data = new_obj_data.get(obj.get_handle(), None)
            if not obj_data or "receptacleObjectIds" not in obj_data:
                continue

            contained_handles = [ self.get_soar_handle(obj_id) for obj_id in obj_data["receptacleObjectIds"] ]
            obj.set_contained_objects(contained_handles)

        self.wm_dirty = True


    #### METHODS TO UPDATE WORKING MEMORY ####
    def is_added(self):
        return (self.objects_id != None)

    def add_to_wm(self, parent_id, svs_commands):
        if self.is_added():
            return 
        self.objects_id = parent_id.CreateIdWME("objects")
        for obj in self.objects.values():
            obj.add_to_wm(self.objects_id, svs_commands)

        self.wm_dirty = False

    def update_wm(self, svs_commands):
        if not self.is_added():
            return
        for obj in self.objects.values():
            if not obj.is_added():
                obj.add_to_wm(self.objects_id, svs_commands)
            else:
                obj.update_wm(svs_commands)
            if obj in self.objs_to_remove:
                self.objs_to_remove.remove(obj)

        for obj in self.objs_to_remove:
            obj.remove_from_wm(svs_commands)
        self.objs_to_remove.clear()
        self.wm_dirty = False

    def remove_from_wm(self, svs_commands):
        if self.is_added():
            for obj in self.objects.values():
                obj.remove_from_wm(svs_commands)
            for obj in self.objs_to_remove:
                if obj not in self.objects.values():
                    obj.remove_from_wm(svs_commands)
            self.objs_to_remove.clear()

            self.objects_id.DestroyWME()
            self.objects_id = None
