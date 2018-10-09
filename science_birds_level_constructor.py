from math import abs
from random import randint

LENGTH_OF_SQUARE_BLOCK_EDGE = 0.43
WIDTH_OF_RECTANGLE = 2.06
HEIGHT_OF_RECTANGLE = 0.22
NUMBER_OF_TILES_PER_EDGE_OF_SQUARE_PLATFORM = 5
PLATFORM_WIDTH = NUMBER_OF_TILES_PER_EDGE_OF_SQUARE_PLATFORM
PLATFORM_HEIGHT = NUMBER_OF_TILES_PER_EDGE_OF_SQUARE_PLATFORM
Y_COORDINATE_OF_GROUND = -3.5


def transpose_and_invert_tiles(mosaic_tiles):
    """
    The mosaic tiles start from top-left and go towards bottom-right. This is
    not practical when constructing a Science Birds level. We want to start
    from bottom-left and go towards top-right. Hence, we transpose and invert
    mosaic tiles.
    """
    return [column[::-1] for column in map(list, zip(*mosaic_tiles))]


def get_block_type(block_name):
    if block_name.startswith('ice'): return 'ice'
    elif block_name.startswith('wood'): return 'wood'
    elif block_name.startswith('stone'): return 'stone'
    else: raise ValueError('Unknown block type for block "{}"'.format(block_name))


def remove_ice_blocks(mosaic_tiles):
    """
    Since ice blocks usually represent whitespace (i.e, background), we want to
    remove them.
    """
    return [[tile for tile in column if get_block_type(tile) != 'ice'] for column in mosaic_tiles]


def platform_intersects_with_existing_platform(new_platform_coordinate, platform_start_coordinates):
    for coordinate in platform_start_coordinates:
        if abs(coordinate[0] - new_platform_coordinate[0]) < PLATFORM_WIDTH and abs(coordinate[1] - new_platform_coordinate[1]) < PLATFORM_HEIGHT:
            return True
    return False


def generate_platform_coordinates(mosaic_tiles):
    """
    Returns a list of coordinates that indicate the starting point of the
    platforms.
    """
    number_of_unsuccessful_attempts_to_get_a_coordinate = 0
    coordinates = []
    while number_of_unsuccessful_attempts_to_get_a_coordinate < 3:
        column_index = randint(0, len(mosaic_tiles) - PLATFORM_WIDTH)
        coordinate = (column_index, randint(0, len(mosaic_tiles[column_index]) - PLATFORM_HEIGHT))
        if not platform_intersects_with_existing_platform(coordinate, coordinates):
            coordinates.append(coordinate)
        else:
            number_of_unsuccessful_attempts_to_get_a_coordinate += 1
    return coordinates


def insert_platform_into_mosaic(mosaic_tiles, coordinate):
    """
    Insert a platform like the following to the structure:
    ------------
    |          |
    |          |
    |          |
    |          |
    ------------
    """
    # 1) Make sure the floor of the platform is complete.
    HEIGHT_OF_PLATFORM_FLOOR = coordinate[1] + 1
    for column_order in range(1, PLATFORM_WIDTH):
        column_index = coordinate[0] + column_order
        while(len(mosaic_tiles[column_index]) < HEIGHT_OF_PLATFORM_FLOOR):
            mosaic_tiles[column_index].append('stone_square_small_1')
    # 2) Construct the walls of the platform if required. Walls are at the
    # first and the last columns.
    for column_order in [0, PLATFORM_WIDTH - 1]:
        column_index = coordinate[0] + column_order
        while(len(mosaic_tiles[column_index]) < HEIGHT_OF_PLATFORM_FLOOR + PLATFORM_HEIGHT - 2):
            mosaic_tiles[column_index].append('stone_square_small_1')
    # 3) Create space in the platform
    for column_order in range(1, PLATFORM_WIDTH - 1):
        column_index = coordinate[0] + column_order
        for row_order in range(1, PLATFORM_HEIGHT - 1):
            row_index = coordinate[1] + row_order
            '''
            This method accounts for going out of bounds of the ceiling.
            Since we are using 'insert', instead of assignment or something
            else, this makes sure that even if we go out of bounds, the
            required element will be appended to the list.
            '''
            mosaic_tiles[column_index].insert(row_index, 'none')
    # 4) Put the rectangle to top-left of the platform.
    mosaic_tiles[coordinate[0]].insert(coordinate[1] + PLATFORM_HEIGHT - 1, 'rectangle-start')
    # 5) Put 'rectangle-continuation' to the rest of the tiles that the
    # rectangle covers.
    for column_order in range(1, PLATFORM_WIDTH):
        mosaic_tiles[coordinate[0] + column_order][coordinate[1] + PLATFORM_HEIGHT - 1] = 'rectangle-continuation'

    return mosaic_tiles


def get_xml_elements_from_mosaic(mosaic_tiles):
    """
    Returns XML elements to generate a Science Birds level.
    """
    elements = ''
    for column_index, column in enumerate(mosaic_tiles):
        current_height = Y_COORDINATE_OF_GROUND
        for tile_index, tile in enumerate(column):
            if 'square_small' in tile:
                elements += '<Block type="SquareSmall" material="{}" x="{}" y="{}" rotation="0"/>\n'.format(get_block_type(tile), column_index * LENGTH_OF_SQUARE_BLOCK_EDGE, current_height)
                current_height += LENGTH_OF_SQUARE_BLOCK_EDGE
            # FIXME Give the rectangle the same name as in the block image
            # names to make it unambiguous which rectange it is. Right now,
            # 'rectangle' means only 'RectBig'. When you allow other types of
            # rectangles, you will need to fix the following 'elif' clause.
            elif 'rectangle' in tile:
                # FIXME Allow rectangle to have different material types apart
                # from stone.
                # FIXME Fix the X position of the rectangle.
                if tile == 'rectangle-start':
                    elements += '<Block type="RectBig" material="{}" x="{}" y="{}" rotation="0"/>\n'.format('stone', column_index * LENGTH_OF_SQUARE_BLOCK_EDGE, current_height)
                current_height += HEIGHT_OF_RECTANGLE
            elif tile == 'none':
                current_height += LENGTH_OF_SQUARE_BLOCK_EDGE
    return elements


def construct_level(mosaic_tiles):
    mosaic_tiles = remove_ice_blocks(transpose_and_invert_tiles(mosaic_tiles))
    platform_coordinates = generate_platform_coordinates(mosaic_tiles)
    for coordinate in platform_coordinates:
        mosaic_tiles = insert_platform_into_mosaic(mosaic_tiles, coordinate)
    with open('blocks.xml', 'w') as f: f.write(get_xml_elements_from_mosaic(mosaic_tiles))
