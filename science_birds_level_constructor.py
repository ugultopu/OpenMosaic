from random import randint

LENGTH_OF_SQUARE_BLOCK_EDGE = 0.43
WIDTH_OF_RECTANGLE = 2.06
HEIGHT_OF_RECTANGLE = 0.22
NUMBER_OF_TILES_PER_EDGE_OF_SQUARE_PLATFORM = 4
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


def platform_intersects_with_existing_platforms(new_platform_coordinate, platform_start_coordinates):
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
        if not platform_intersects_with_existing_platforms(coordinate, coordinates):
            coordinates.append(coordinate)
        else:
            number_of_unsuccessful_attempts_to_get_a_coordinate += 1
    # Sort coordinates ascending w.r.t X coordinate.
    coordinates.sort(key = lambda coordinate: coordinate[0])
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
    # FIXME It seems like the possibly extra columns are not added to the end
    # of mosaic_tiles. Need to check it out how this is possible without
    # getting an "IndexError: list index out of range" error. Realized this by
    # print out the phases of "get_column_X_distances".

    # 1) Make sure that the height of all columns of the platform are
    # sufficient.
    HEIGHT_UNTIL_PLATFORM_CEILING = coordinate[1] + PLATFORM_HEIGHT
    for column_order in range(PLATFORM_WIDTH):
        column_index = coordinate[0] + column_order
        while(len(mosaic_tiles[column_index]) < HEIGHT_UNTIL_PLATFORM_CEILING):
            mosaic_tiles[column_index].append('stone_square_small_1')
    # 2) Replace the tiles in center with 'none' tiles.
    for column_order in range(1, PLATFORM_WIDTH - 1):
        column_index = coordinate[0] + column_order
        for row_order in range(1, PLATFORM_HEIGHT - 1):
            row_index = coordinate[1] + row_order
            mosaic_tiles[column_index][row_index] = 'none'
    # 3) Replace the tile on top-left of the platform with 'rectangle-start'
    # (that is, "RectBig") tile.
    mosaic_tiles[coordinate[0]][coordinate[1] + PLATFORM_HEIGHT - 1] = 'rectangle-start'
    # 4) Replace the tiles on top with 'rectangle-continuation tiles'.
    for column_order in range(1, PLATFORM_WIDTH):
        mosaic_tiles[coordinate[0] + column_order][coordinate[1] + PLATFORM_HEIGHT - 1] = 'rectangle-continuation'

    return mosaic_tiles


def get_column_X_distances(mosaic_tiles, platform_coordinates):
    """
    Compute the X distances from origin of column starting points, taking into
    account of the extra space covered by rectangle blocks on top of platforms.
    """
    x_distances = []
    for column_index, column in enumerate(mosaic_tiles):
        distance = column_index * LENGTH_OF_SQUARE_BLOCK_EDGE
        print 'platform coordinates are:'
        print platform_coordinates
        if column_index - PLATFORM_WIDTH == platform_coordinates[0][0]:
            distance += WIDTH_OF_RECTANGLE % LENGTH_OF_SQUARE_BLOCK_EDGE
            # The following while loop accounts for having multiple platforms
            # starting at the same column.
            while column_index - PLATFORM_WIDTH == platform_coordinates[0][0]:
                del platform_coordinates[0]
        x_distances.append(distance)

    return x_distances



def get_xml_elements_from_mosaic(mosaic_tiles, column_x_distances):
    """
    Returns XML elements to generate a Science Birds level.
    """
    elements = ''
    for column_index, column in enumerate(mosaic_tiles):
        current_height = Y_COORDINATE_OF_GROUND
        for tile_index, tile in enumerate(column):
            # FIXME Give the rectangle the same name as in the block image
            # names to make it unambiguous which rectange it is. Right now,
            # 'rectangle' means only 'RectBig'. When you allow other types of
            # rectangles, you will need to fix the following 'elif' clause.
            if tile.startswith('rectangle'):
                # FIXME Allow rectangle to have different material types apart
                # from stone.
                if tile == 'rectangle-start':
                    elements += '<Block type="RectBig" material="{}" x="{}" y="{}" rotation="0"/>\n'.format('stone', column_x_distances[column_index] - WIDTH_OF_RECTANGLE % LENGTH_OF_SQUARE_BLOCK_EDGE / 2, current_height)
                current_height += HEIGHT_OF_RECTANGLE
            elif tile == 'none':
                current_height += LENGTH_OF_SQUARE_BLOCK_EDGE
            # FIXME The mosaic generator generates all kinds of blocks (square,
            # triangle, rectangle, etc.). However, we actually need to convert
            # all of these blocks to "SquareSmall" before making any operations
            # on mosaic tiles. However, to save time, I didn't write the
            # conversion function yet. In this 'else' clause, I say that if a
            # tile is not a rectangle or "none", than it should be a square.
            #
            # I need to convert the tiles in the future to prevent possible
            # bugs.
            else:
                elements += '<Block type="SquareSmall" material="{}" x="{}" y="{}" rotation="0"/>\n'.format(get_block_type(tile), column_x_distances[column_index], current_height)
                current_height += LENGTH_OF_SQUARE_BLOCK_EDGE
    return elements


def construct_level(mosaic_tiles):
    mosaic_tiles = remove_ice_blocks(transpose_and_invert_tiles(mosaic_tiles))
    platform_coordinates = generate_platform_coordinates(mosaic_tiles)
    for coordinate in platform_coordinates:
        mosaic_tiles = insert_platform_into_mosaic(mosaic_tiles, coordinate)
    column_x_distances = get_column_X_distances(mosaic_tiles, platform_coordinates)
    with open('blocks.xml', 'w') as f: f.write(get_xml_elements_from_mosaic(mosaic_tiles, column_x_distances))
