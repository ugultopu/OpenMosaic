LENGTH_OF_SQUARE_BLOCK_EDGE = 0.43
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
