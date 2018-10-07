from random import randint

LENGTH_OF_SQUARE_BLOCK_EDGE = 0.43
WIDTH_OF_RECTANGLE = 2.06
HEIGHT_OF_RECTANGLE = 0.22
NUMBER_OF_TILES_PER_EDGE_OF_SQUARE_PLATFORM = 5
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
    for coordinates in new_platform_coordinate:
        if abs(coordinates[0] - new_platform_coordinate[0]) < NUMBER_OF_TILES_PER_EDGE_OF_SQUARE_PLATFORM and abs(coordinates[1] - new_platform_coordinate[1]) < NUMBER_OF_TILES_PER_EDGE_OF_SQUARE_PLATFORM:
            return True
    return False


def get_platform_coordinates(mosaic_tiles):
    """
    Returns a list of coordinates that indicate the starting point of the
    platforms.
    """
    number_of_unsuccessful_attempts_to_get_a_coordinate = 0
    coordinates = []
    while number_of_unsuccessful_attempts_to_get_a_coordinate < 3:
        coordinate = (randint(0, len(mosaic_tiles) - 1 - NUMBER_OF_TILES_PER_EDGE_OF_SQUARE_PLATFORM), randint(NUMBER_OF_TILES_PER_EDGE_OF_SQUARE_PLATFORM - 1, len(mosaic_tiles[column_index]) - 1))
        if not platform_overlap_with_existing_platform(coordinate, coordinates):
            coordinates.append(coordinate)
        else:
            number_of_unsuccessful_attempts_to_get_a_coordinate += 1
    return coordinates


def get_xml_elements_from_mosaic(mosaic_tiles):
    """
    Returns XML elements to generate a Science Birds level.
    """
    elements = ''
    for column_index, column in enumerate(mosaic_tiles):
        for tile_index, tile in enumerate(column): elements += '<Block type="SquareSmall" material="{}" x="{}" y="{}" rotation="0"/>\n'.format(get_block_type(tile), column_index * LENGTH_OF_SQUARE_BLOCK_EDGE, tile_index * LENGTH_OF_SQUARE_BLOCK_EDGE + Y_COORDINATE_OF_GROUND)
    return elements


def construct_level(mosaic_tiles):
    with open('blocks.xml', 'w') as f: f.write(get_xml_elements_from_mosaic(remove_ice_blocks(transpose_and_invert_tiles(mosaic_tiles))))
