import logging as log
from bisect import bisect_left
from random import randrange, sample

from science_birds_blocks import block_registry


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
    else: log.warning('Unknown block type for block %s', block)


def remove_ice_blocks(blocks):
    """
    Since ice blocks usually represent whitespace (i.e, background), we want to
    remove them.
    """
    return [[block for block in column if get_block_type(block) != 'ice'] for column in blocks]


def staticinit(cls):
    """A decorator for static initialization."""
    cls.init_static()
    return cls


@staticinit
class Structure:
    """ A building-like structure for Science Birds.

    This does not represent a whole Science Birds level. It represents only a
    structure in a Science Birds level.

    Blocks are represented in a matrix (that is, a list of lists). Each row of
    the matrix represents a column of the structure. That is, the matrix
    represents the structure starting from bottom-left and goes towards
    top-right, by going up the column first, then to the next column.
    """
    """ "Principal Block" is the block that is most frequently used to construct
    the structure. It can be a Hollow Square, Tiny Square, Tiny Rectangle,
    Small Rectangle, etc. """
    PRINCIPAL_BLOCK = 'tiny_square'
    RECTANGLE_WIDTH = block_registry['long_rectangle']['width']
    RECTANGLE_HEIGHT = block_registry['long_rectangle']['height']
    PIG_WIDTH = 0.5
    GROUND_HEIGHT = -3.5
    PLATFORM_RATIO = .5
    "Ratio of number of platforms over total height of the shortest column."
    BLOCK_STRING = '<Block type="{}" material="{}" x="{}" y="{}" rotation="{}"/>\n'


    @classmethod
    def init_static(cls):
        cls.PRINCIPAL_BLOCK_WIDTH = block_registry[cls.PRINCIPAL_BLOCK]['width']
        cls.PRINCIPAL_BLOCK_HEIGHT = block_registry[cls.PRINCIPAL_BLOCK]['height']
        cls.calculate_center_indices_for_rectangle()


    @classmethod
    # FIXME This algorithm might not be exactly correct. For example, for Hollow
    # Squares as principle blocks, if one hollow square is placed right in the
    # middle of the rectangle, the rectangle will cover only 2 more rectangles
    # (and it will cover them partly, as expected), instead of covering 4
    # rectangles in total. So, you might need to do the calculation on a
    # case-by-case basis for each rectangle. This is computationally much more
    # expensive though. Think of a solution for this.
    def calculate_center_indices_for_rectangle(cls):
        cls.CENTER_INDICES_OF_RECTANGLE = []
        NUMBER_OF_PRINCIPAL_BLOCKS_COVERED_BY_RECTANGLE = int(cls.RECTANGLE_WIDTH / cls.PRINCIPAL_BLOCK_WIDTH) + 1 + 1 if cls.RECTANGLE_WIDTH % cls.PRINCIPAL_BLOCK_WIDTH != 0 else 0
        CENTER = int(NUMBER_OF_PRINCIPAL_BLOCKS_COVERED_BY_RECTANGLE / 2)
        for index in range(int(cls.PIG_WIDTH / cls.PRINCIPAL_BLOCK_WIDTH) + 1):
            half_of_index = int(index / 2)
            if index % 2 == 0:
                cls.CENTER_INDICES_OF_RECTANGLE.append(CENTER + half_of_index)
            else:
                cls.CENTER_INDICES_OF_RECTANGLE.append(CENTER - half_of_index - 1)


    def __init__(self, blocks, platforms=None):
        self.blocks = remove_ice_blocks(transpose_and_invert_blocks(blocks))
        self.STRUCTURE_WIDTH = self.PRINCIPAL_BLOCK_WIDTH * len(self.blocks)
        self.NUMBER_OF_RECTANGLES = int(self.STRUCTURE_WIDTH / self.RECTANGLE_WIDTH) + 1
        self.SHORTEST_COLUMN_HEIGHT = len(min(self.blocks, key=len))
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


    def get_rectangle_start_distance(self, index):
        """
        Get X distance for the start point of the rectangle at the given index.
        """
        return -(self.NUMBER_OF_RECTANGLES * self.RECTANGLE_WIDTH - self.STRUCTURE_WIDTH) / 2 + index * self.RECTANGLE_WIDTH


    def get_column_indices_for_gaps(self):
        failed_attempts = 0
        columns = []
        # FIXME Refactor the magic number "3" below into a constant or
        # expression.
        while failed_attempts < 3:
            rectangle_index = randrange(1, self.NUMBER_OF_RECTANGLES - 1)
            column = int(self.get_rectangle_start_distance(rectangle_index) / self.PRINCIPAL_BLOCK_WIDTH)
            if column not in columns:
                columns.append(column)
            else:
                failed_attempts += 1
        return columns

    # Not being used right now, but might be used in the future.
    def insert_gaps_until_top(self, columns):
        for column in columns:
            for center in self.CENTER_INDICES_OF_RECTANGLE:
                for row in range(len(self.blocks[column + center])):
                    if self.blocks[column + center][row] != 'platform':
                        self.blocks[column + center][row] = 'none'


    def insert_gaps_until_top_platform(self, columns):
        for column in columns:
            for row in range(self.platforms[-1]):
                if self.blocks[column][row] != 'platform':
                    for center in self.CENTER_INDICES_OF_RECTANGLE:
                        self.blocks[column + center][row] = 'none'


    def get_height_of_block(self, row):
        """
        Assumes the "platforms" are sorted and the blocks in "platforms" have
        been placed in "blocks".
        """
        NUMBER_OF_PLATFORMS = bisect_left(self.platforms, row)
        return self.GROUND_HEIGHT + (row - NUMBER_OF_PLATFORMS) * self.PRINCIPAL_BLOCK_HEIGHT + NUMBER_OF_PLATFORMS * self.RECTANGLE_HEIGHT


    def get_xml_elements_for_principal_blocks(self):
        """
        Returns XML elements to generate a Science Birds level.
        """
        elements = ''
        for column_index, column in enumerate(self.blocks):
            for block_index, block in enumerate(column):
                if block not in ['platform', 'none']:
                    elements += self.BLOCK_STRING.format(block_registry[self.PRINCIPAL_BLOCK]['xml_name'],
                                                         get_block_type(block),
                                                         column_index * self.PRINCIPAL_BLOCK_WIDTH + self.PRINCIPAL_BLOCK_WIDTH / 2,
                                                         self.get_height_of_block(block_index) + self.PRINCIPAL_BLOCK_HEIGHT / 2,
                                                         0)
        return elements


    def get_xml_elements_for_rectangle_blocks(self):
        elements = ''
        for platform in self.platforms:
            for index in range(self.NUMBER_OF_RECTANGLES):
                elements += self.BLOCK_STRING.format(block_registry['long_rectangle']['xml_name'],
                                                     'stone',
                                                     self.get_rectangle_start_distance(index) + self.RECTANGLE_WIDTH / 2,
                                                     self.get_height_of_block(platform) + self.RECTANGLE_HEIGHT / 2,
                                                     0)
        return elements


    def construct_level(self):
        self.insert_gaps_until_top_platform(self.get_column_indices_for_gaps())
        principal_block_elements = self.get_xml_elements_for_principal_blocks()
        rectangle_elements = self.get_xml_elements_for_rectangle_blocks()
        with open('blocks.xml', 'w') as structure_xml_file:
            structure_xml_file.write(principal_block_elements + rectangle_elements)


if __name__ == '__main__':
    TEST_BLOCKS = [
        ['stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square'],
        ['platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform'],
        ['stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square'],
        ['platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform'],
        ['stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square']
    ]
    Structure(TEST_BLOCKS, [1, 3]).construct_level()
