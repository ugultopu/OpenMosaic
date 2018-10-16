import logging as log
from bisect import bisect_left
from random import randrange, sample


def transpose_and_invert_blocks(blocks):
    """
    The blocks blocks start from top-left and go towards bottom-right. This is
    not practical when constructing a Science Birds level. We want to start
    from bottom-left and go towards top-right. Hence, we transpose and invert
    blocks blocks.
    """
    return [column[::-1] for column in map(list, zip(*blocks))]


def get_block_type(block):
    if block.startswith('ice'): return 'ice'
    elif block.startswith('wood'): return 'wood'
    elif block.startswith('stone'): return 'stone'
    else: log.warning('Unknown block type for block "{}"'.format(block))


def remove_ice_blocks(blocks):
    """
    Since ice blocks usually represent whitespace (i.e, background), we want to
    remove them.
    """
    return [[block for block in column if get_block_type(block) != 'ice'] for column in blocks]


def get_center_indices_for_rectangle(rectangle_width, square_dimension):
    SQUARES_COVERED_BY_RECTANGLE = int(rectangle_width / square_dimension) + 1 + 1 if rectangle_width % square_dimension != 0 else 0
    CENTER = int(SQUARES_COVERED_BY_RECTANGLE / 2)
    return [CENTER] if SQUARES_COVERED_BY_RECTANGLE % 2 == 1 else [CENTER - 1, CENTER]


class Structure:
    """ A building-like structure for Science Birds.

    This does not represent a whole Science Birds level. It represents only a
    structure in a Science Birds level.

    Blocks are represented in a matrix (that is, a list of lists). Each row of
    the matrix represents a column of the structure. That is, the matrix
    represents the structure starting from bottom-left and goes towards
    top-right, by going up the column first, then to the next column.
    """
    SQUARE_DIMENSION = 0.43
    RECTANGLE_WIDTH = 2.06
    RECTANGLE_HEIGHT = 0.22
    CENTER_INDICES_OF_RECTANGLE = get_center_indices_for_rectangle(RECTANGLE_WIDTH, SQUARE_DIMENSION)
    GROUND_HEIGHT = -3.5
    PLATFORM_RATIO = .3
    "Ratio of number of platforms over total height of the shortest column."


    def __init__(self, blocks, platforms=None):
        self.blocks = remove_ice_blocks(transpose_and_invert_blocks(blocks))
        self.STRUCTURE_WIDTH = self.SQUARE_DIMENSION * len(self.blocks)
        self.NUMBER_OF_RECTANGLES = int(self.STRUCTURE_WIDTH / self.RECTANGLE_WIDTH) + 1
        self.SHORTEST_COLUMN_HEIGHT = len(min(self.blocks, key=lambda column: len(column)))
        if platforms is None:
            platforms = self.generate_platforms()
            self.insert_platforms(platforms)
        self.platforms = platforms


    def generate_platforms(self):
        return sorted(sample(range(self.SHORTEST_COLUMN_HEIGHT), int(self.PLATFORM_RATIO * self.SHORTEST_COLUMN_HEIGHT)))


    def insert_platforms(self, platforms):
        for platform in platforms:
            for column in self.blocks:
                column[platform] = 'platform'


    def get_xml_elements_for_square_blocks(self):
        """
        Returns XML elements to generate a Science Birds level.
        """
        elements = ''
        for column_index, column in enumerate(self.blocks):
            for block_index, block in enumerate(column):
                if block != 'platform' and block != 'none':
                    elements += '<Block type="SquareSmall" material="{}" x="{}" y="{}" rotation="0"/>\n'.format(get_block_type(block), column_index * self.SQUARE_DIMENSION + self.SQUARE_DIMENSION / 2, self.get_height_of_block(block_index) + self.SQUARE_DIMENSION / 2)
        return elements


    def get_rectangle_start_distance(self, index):
        """
        Get the X distance for rectangle start.
        """
        return -(self.NUMBER_OF_RECTANGLES * self.RECTANGLE_WIDTH - self.STRUCTURE_WIDTH) / 2 + index * self.RECTANGLE_WIDTH


    def get_height_of_block(self, row):
        """
        Assumes the "platforms" are sorted and the blocks in "platforms" have
        been placed in "blocks".
        """
        NUMBER_OF_PLATFORMS = bisect_left(self.platforms, row)
        return self.GROUND_HEIGHT + (row - NUMBER_OF_PLATFORMS) * self.SQUARE_DIMENSION + NUMBER_OF_PLATFORMS * self.RECTANGLE_HEIGHT


    def get_xml_elements_for_rectangle_blocks(self):
        elements = ''
        for platform in self.platforms:
            for index in range(self.NUMBER_OF_RECTANGLES):
                elements += '<Block type="RectBig" material="{}" x="{}" y="{}" rotation="0"/>\n'.format('stone', self.get_rectangle_start_distance(index) + self.RECTANGLE_WIDTH / 2, self.get_height_of_block(platform) + self.RECTANGLE_HEIGHT / 2)
        return elements


    def get_column_index_for_gaps(self):
        rectangle_index = randrange(1, self.NUMBER_OF_RECTANGLES - 1)
        column_index = self.get_rectangle_start_distance(rectangle_index) / self.SQUARE_DIMENSION
        return int(column_index)


    def insert_gaps_until_top_platform(self, column):
        for row in range(self.platforms[-1]):
            if self.blocks[column][row] != 'platform':
                for center in self.CENTER_INDICES_OF_RECTANGLE:
                    self.blocks[column + center][row] = 'none'


    def construct_level(self):
        # TODO Call "insert_gaps_until_top_platform" in a loop to insert gaps to
        # more columns.
        self.insert_gaps_until_top_platform(self.get_column_index_for_gaps())
        square_elements = self.get_xml_elements_for_square_blocks()
        rectangle_elements = self.get_xml_elements_for_rectangle_blocks()
        with open('blocks.xml', 'w') as f: f.write(square_elements + rectangle_elements)


if __name__ == '__main__':
    test_blocks = [
                    ['stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square'],
                    ['platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform'],
                    ['stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square'],
                    ['platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform'],
                    ['stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square']
                  ]
    Structure(test_blocks, [1,3]).construct_level()
