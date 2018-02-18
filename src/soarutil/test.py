from SVSCommands import SVSCommands

print SVSCommands.pos_to_str([3.1, 4.1, 5.9])
print SVSCommands.rot_to_str([3.1, 4.1, 5.9])
print SVSCommands.scl_to_str([3.1, 4.1, 5.9])

print SVSCommands.add_box("box1", [1, 2, 3], [4, 5, 6])
print SVSCommands.add_box("box2")

print SVSCommands.change_pos("box2", [1, 2, 3])
print SVSCommands.add_tag("box2", "color", "red")
print SVSCommands.change_pos("box2", [1, 2, 3])
