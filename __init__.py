import bpy
from pathlib import Path

bl_info = {
    "name": "Taremin Outliner Sync Active",
    "category": "3D View",
    "author": "Taremin",
    "location": "View 3D > Taremin",
    "description": "Show active object in outliner when active object is changed",
    "version": (0, 0, 1),
    "blender": (3, 20, 0),
    "wiki_url": "",
    "tracker_url": "",
    "warning": "",
}

owner = object()


def outliner_show_active(*args):
    context = bpy.context
    for window in context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type != "OUTLINER":
                continue
            for region in area.regions:
                if region.type != "WINDOW":
                    continue
                with context.temp_override(window=window, area=area, region=region):
                    bpy.ops.outliner.show_active()


def on_change_active(*args):
    outliner_show_active(*args)


def subscribe():
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, "active"),
        owner=owner,
        args=tuple(),
        notify=on_change_active,
    )


def unsubscribe():
    bpy.msgbus.clear_by_owner(owner)


class TAREMIN_OUTLINER_SYNC_ACTIVE_Props(bpy.types.PropertyGroup):
    def update_is_active(self, context):
        if self.is_active:
            subscribe()
        else:
            unsubscribe()

    def on_unregister(self):
        self["is_active"] = False

    is_active: bpy.props.BoolProperty(default=False, update=update_is_active)


class TAREMIN_OUTLINER_SYNC_ACTIVE_PT_Panel(bpy.types.Panel):
    bl_label = "Taremin Outliner Sync Active"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_category = "Taremin"

    def draw(self, context):
        settings = context.scene.taremin_osa
        layout = self.layout
        row = layout.row()
        row.prop(settings, "is_active", text="Active")


classes = (TAREMIN_OUTLINER_SYNC_ACTIVE_Props, TAREMIN_OUTLINER_SYNC_ACTIVE_PT_Panel)


def register():
    for value in classes:
        retry = 0
        while True:
            try:
                bpy.utils.register_class(value)
                break
            except ValueError:
                bpy.utils.unregister_class(value)
                retry += 1
                if retry > 1:
                    break
    bpy.types.Scene.taremin_osa = bpy.props.PointerProperty(
        type=TAREMIN_OUTLINER_SYNC_ACTIVE_Props
    )


def unregister():
    for value in classes:
        try:
            bpy.utils.unregister_class(value)
        except RuntimeError:
            pass

    bpy.context.scene.taremin_osa.on_unregister()
    unsubscribe()
    del bpy.types.Scene.taremin_osa
    Path(__file__).touch()


if __name__ == "__main__":
    register()
