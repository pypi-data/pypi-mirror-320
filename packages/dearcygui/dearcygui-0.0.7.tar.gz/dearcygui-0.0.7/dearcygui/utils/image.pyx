cimport dearcygui as dcg

from dearcygui.c_types cimport unique_lock, recursive_mutex
from libcpp.map cimport map, pair
from libcpp.set cimport set
from libcpp.vector cimport vector
from cython.operator cimport dereference
from cpython.ref cimport PyObject, Py_INCREF, Py_DECREF


import numpy as np

cdef struct TileData:
    """
    Data structure to store the tile data.
    """
    double xmin # We store as double to avoid rounding overhead during draw
    double xmax
    double ymin
    double ymax
    int width
    int height
    bint show
    PyObject *texture

cdef class TiledImage(dcg.drawingItem):
    """
    This item enables to easily display a possibly huge
    image by only loading the image times that are currently
    visible.

    The texture management is handled implicitly.
    """

    cdef double margin
    cdef map[long long, TileData] _tiles
    cdef set[pair[int, int]] _requested_tiles

    def __cinit__(self):
        self.margin = 128

    def __dealloc__(self):
        cdef pair[int, TileData] *tile_data
        for tile_data in self._tiles:
            Py_DECREF(tile_data.second.texture)

    @property
    def margin(self):
        """
        Margin in pixels around the visible area for
        the area that is loaded in advance.
        """
        return self.margin

    def add_tile(self,
                 content,
                 coord,
                 opposite_coord=None,
                 visible=True):
        """
        Add a tile to the list of tiles.
        Inputs:
            content: numpy array, the content of the tile
            coord: the top-left coordinate of the tile
            opposite_coord (optional): if not given,
                defaults to coord + content.shape.
                Else corresponds to the opposite coordinate
                of the tile.
            visible (optional): whether the tile should start visible or not.
        Outputs:
            Unique uuid of the tile.
        """
        cdef unique_lock[recursive_mutex] m
        content = np.asarray(content)
        assert content.ndim == 2 or content.ndim == 3
        if content.ndim == 3:
            assert content.shape[2] <= 4

        cdef double[2] top_left = dcg.read_coord(coord)
        cdef double[2] bottom_right
        if opposite_coord is None:
            bottom_right[0] = top_left[0] + content.shape[1]
            bottom_right[1] = top_left[1] + content.shape[0]
        else:
            bottom_right = dcg.read_coord(opposite_coord)
        cdef dcg.Texture texture = dcg.Texture(self.context, content)
        cdef long long uuid = self.context.next_uuid.fetch_add(1)
        cdef TileData tile
        tile.xmin = top_left[0]
        tile.xmax = bottom_right[0]
        tile.ymin = top_left[1]
        tile.ymax = bottom_right[1]
        tile.width = content.shape[1]
        tile.height = content.shape[0]
        tile.show = visible
        Py_INCREF(<PyObject*>texture)
        tile.texture = <PyObject*>texture
        # No need to block rendering before adding the tile
        m = unique_lock[recursive_mutex](self.mutex)
        cdef pair[long long, TileData] tile_data = (uuid, tile)
        self._tiles.insert(tile_data)
        return uuid

    def remove_tile(self, uuid) -> None:
        """
        Remove a tile from the list of tiles.
        Inputs:
            uuid: the unique identifier of the tile.
        """
        cdef unique_lock[recursive_mutex] m = unique_lock[recursive_mutex](self.mutex)
        cdef map[int, TileData].iterator tile_data = self._tiles.find(uuid)
        if tile_data != self._tiles.end():
            Py_DECREF(dereference(tile_data).second.texture)
            self._tiles.erase(tile_data)
        else:
            raise ValueError("Tile not found")

    def set_tile_visibility(self, uuid, visible) -> None:
        """
        Set the visibility status of a tile.
        Inputs:
            uuid: the unique identifier of the tile.
            visible: Whether the tile should be visible or not.
        By default tiles start visible.
        """
        cdef unique_lock[recursive_mutex] m = unique_lock[recursive_mutex](self.mutex)
        cdef map[int, TileData].iterator tile_data = self._tiles.find(uuid)
        if tile_data != self._tiles.end():
            dereference(tile_data).second.show = visible
        else:
            raise ValueError("Tile not found")

    def update_tile(self, uuid, content : np.ndarray) -> None:
        """
        Update the content of a tile.
        Inputs:
            uuid: the unique identifier of the tile.
            content: the new content of the tile.
        """
        cdef unique_lock[recursive_mutex] m = unique_lock[recursive_mutex](self.mutex)
        cdef map[int, TileData].iterator tile_data = self._tiles.find(uuid)
        cdef pair[int, TileData] *tile
        if tile_data != self._tiles.end():
            tile = dereference(tile_data)
            (<dcg.Texture>tile.second.texture).set_value(content)
        else:
            raise ValueError("Tile not found")

    cdef void draw(self, void* drawlist) noexcept nogil:
        cdef unique_lock[recursive_mutex] m = unique_lock[recursive_mutex](self.mutex)
        # Retrieve min/max visible area

        cdef double xmin, xmax, ymin, ymax
        # top left of the drawing area
        cdef float[2] start, end
        start[0] = self.context.viewport.parent_pos.x
        start[1] = self.context.viewport.parent_pos.y
        end[0] = start[0] + self.context.viewport.parent_size.x
        end[1] = start[1] + self.context.viewport.parent_size.y
        cdef double[2] start_coord, end_coord
        self.context.viewport.screen_to_coordinate(start_coord, start)
        self.context.viewport.screen_to_coordinate(end_coord, end)
        # the min/max are because there could be
        # inversions in the screen to coordinate transform.
        xmin = min(start_coord[0], end_coord[0])
        xmax = max(start_coord[0], end_coord[0])
        ymin = min(start_coord[1], end_coord[1])
        ymax = max(start_coord[1], end_coord[1])

        # Display each tile already loaded that are visible:
        cdef pair[int, TileData] *tile_data
        cdef TileData *tile
        for tile_data in self._tiles:
            tile = tile_data.second
            if tile.xmin < xmax and tile.xmax > xmin and tile.ymin < ymax and tile.ymax > ymin and tile.show:
                # Draw the tile
                dcg.imgui.draw_image_quad(self.context,
                                          (<dcg.Texture>tile.texture).allocated_texture,
                                          tile.xmin, tile.ymin,
                                          tile.xmax, tile.ymin,
                                          tile.xmax, tile.ymax,
                                          tile.xmin, tile.ymax,
                                          0., 0.,
                                          1., 0.,
                                          1., 1.,
                                          0., 1.,
                                          4294967295)

        return
