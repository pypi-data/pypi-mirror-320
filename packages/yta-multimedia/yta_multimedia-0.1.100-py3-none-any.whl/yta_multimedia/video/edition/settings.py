"""
I'm placing the edition settings here until I find
a better place, but I want to keep them in the same
file by now to avoid duplicating them in the files
I am building for new concepts.

TODO: Move this to a definitive file in a near 
future, please
"""
# TODO: This must be read from another file which is
# not the 'image_editor' to avoid possible cyclic
# import issues
from yta_multimedia.image.edition.image_editor import COLOR_TEMPERATURE_CHANGE_LIMIT


LAYERS_INDEXES_LIMIT = (0, 9)
"""
The limit of the layers indexes we have, starting
from 0, so only the upper limit + 1 layers are
available in the edition system.
"""
VOLUME_LIMIT = (0, 300)
"""
The limit of the volumen adjustment. Zero (0) means
silence, 100 means the original audio volume and
300 means 3 times higher volume.
"""
ZOOM_LIMIT = (1, 500)
"""
The limit of the zoom adjustment. One (1) means a
zoom out until the video is a 1% of its original 
size, 100 means the original size and 500 means a
zoom in to reach 5 times the original video size.
"""
COLOR_TEMPERATURE_LIMIT = COLOR_TEMPERATURE_CHANGE_LIMIT
"""
The limit of the color temperature adjustment. Zero
(0) means no change, while -50 means...

TODO: Fulfill this as it depends on another const
"""