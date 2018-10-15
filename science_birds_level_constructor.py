import logging as log
from bisect import bisect_left
from random import sample

SQUARE_DIMENSION = 0.43
RECTANGLE_WIDTH = 2.06
RECTANGLE_HEIGHT = 0.22
GROUND_HEIGHT = -3.5
# Ratio of number of platforms over total height of the shortest column.
PLATFORM_RATIO = .3


def transpose_and_invert_tiles(mosaic):
    """
    The mosaic tiles start from top-left and go towards bottom-right. This is
    not practical when constructing a Science Birds level. We want to start
    from bottom-left and go towards top-right. Hence, we transpose and invert
    mosaic tiles.
    """
    return [column[::-1] for column in map(list, zip(*mosaic))]


def get_block_type(block_name):
    if block_name.startswith('ice'): return 'ice'
    elif block_name.startswith('wood'): return 'wood'
    elif block_name.startswith('stone'): return 'stone'
    else: log.warning('Unknown block type for block "{}"'.format(block_name))


def remove_ice_blocks(mosaic):
    """
    Since ice blocks usually represent whitespace (i.e, background), we want to
    remove them.
    """
    return [[tile for tile in column if get_block_type(tile) != 'ice'] for column in mosaic]


def generate_platforms(mosaic):
    SHORTEST_COLUMN_HEIGHT = len(min(mosaic, key=lambda column: len(column)))
    return sorted(sample(range(SHORTEST_COLUMN_HEIGHT), int(PLATFORM_RATIO * SHORTEST_COLUMN_HEIGHT)))


def insert_platforms_into_mosaic(mosaic, platforms):
    for platform in platforms:
        for column in mosaic:
            column[platform] = 'platform'
    return mosaic


def get_height_for_block(row, platforms):
    """
    Assumes the "platforms" are sorted and the blocks in "platforms" have been
    placed in "mosaic".
    """
    NUMBER_OF_PLATFORMS = bisect_left(platforms, row)
    return GROUND_HEIGHT + (row - NUMBER_OF_PLATFORMS) * SQUARE_DIMENSION + NUMBER_OF_PLATFORMS * RECTANGLE_HEIGHT


def get_xml_elements_for_square_blocks(mosaic, platforms):
    """
    Returns XML elements to generate a Science Birds level.
    """
    elements = ''
    for column_index, column in enumerate(mosaic):
        for tile_index, tile in enumerate(column):
            if tile != 'platform' and tile != 'none':
                elements += '<Block type="SquareSmall" material="{}" x="{}" y="{}" rotation="0"/>\n'.format(get_block_type(tile), column_index * SQUARE_DIMENSION + SQUARE_DIMENSION / 2, get_height_for_block(tile_index, platforms) + SQUARE_DIMENSION / 2)
    return elements


def get_xml_elements_for_rectangle_blocks(mosaic, platforms):
    PLATFORM_WIDTH = SQUARE_DIMENSION * len(mosaic)
    NUMBER_OF_RECTANGLES = int(PLATFORM_WIDTH / RECTANGLE_WIDTH) + 1
    elements = ''
    for platform in platforms:
        for index in range(NUMBER_OF_RECTANGLES):
            elements += '<Block type="RectBig" material="{}" x="{}" y="{}" rotation="0"/>\n'.format('stone', -(NUMBER_OF_RECTANGLES * RECTANGLE_WIDTH - PLATFORM_WIDTH) / 2 + index * RECTANGLE_WIDTH + RECTANGLE_WIDTH / 2, get_height_for_block(platform, platforms) + RECTANGLE_HEIGHT / 2)
    return elements


def construct_level(mosaic, platforms=None):
    mosaic = remove_ice_blocks(transpose_and_invert_tiles(mosaic))
    if platforms is None:
        platforms = generate_platforms(mosaic)
    insert_platforms_into_mosaic(mosaic, platforms)
    square_elements = get_xml_elements_for_square_blocks(mosaic, platforms)
    rectangle_elements = get_xml_elements_for_rectangle_blocks(mosaic, platforms)
    with open('blocks.xml', 'w') as f: f.write(square_elements + rectangle_elements)


if __name__ == '__main__':
    test_mosaic = [
                    ['stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square'],
                    ['platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform'],
                    ['stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square'],
                    ['platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform'],
                    ['stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square']
                  ]
    construct_level(test_mosaic, [1,3])
