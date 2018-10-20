import logging as log
from bisect import bisect_left
from random import randrange

from constants import (BLOCK_REGISTRY,
                       GROUND_HEIGHT,
                       BLOCK_STRING,
                       PIG_STRING,
                       LEVEL_TEMPLATE)


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


class Structure:
    """ A building-like structure for Science Birds.

    This does not represent a whole Science Birds level. It represents only a
    structure in a Science Birds level.

    Blocks are represented in a matrix (that is, a list of lists). Each row of
    the matrix represents a column of the structure. That is, the matrix
    represents the structure starting from bottom-left and goes towards
    top-right, by going up the column first, then to the next column.
    """


    def __init__(self,
                 level_path,
                 principal_block,
                 platform_block,
                 blocks,
                 platforms=None):
        self.LEVEL_PATH = level_path
        self.PRINCIPAL_BLOCK = principal_block
        """ PRINCIPAL_BLOCK is the block that is most frequently used to
            construct the structure. Examples can be:
            - Hollow Square
            - Tiny Square
            - Tiny Rectangle
            - Small Rectangle
            etc. """
        self.PLATFORM_BLOCK = platform_block
        self.calculate_center_indices_of_platform_block()
        self.blocks = remove_ice_blocks(transpose_and_invert_blocks(blocks))
        self.STRUCTURE_WIDTH = BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].width * len(self.blocks)
        self.BLOCKS_PER_PLATFORM = int(self.STRUCTURE_WIDTH / BLOCK_REGISTRY[self.PLATFORM_BLOCK].width) + 1
        self.SHORTEST_COLUMN_HEIGHT = len(min(self.blocks, key=len))
        if platforms is None:
            platforms = self.generate_platforms()
            self.insert_platforms(platforms)
        self.platforms = platforms


    # FIXME This algorithm might not be exactly correct. For example, for Hollow
    # Squares as principle blocks, if one hollow square is placed right in the
    # middle of the platform block, the platform block will cover only 2 more platform blocks
    # (and it will cover them partly, as expected), instead of covering 4
    # platform blocks in total. So, you might need to do the calculation on a
    # case-by-case basis for each platform block. This is computationally much more
    # expensive though. Think of a solution for this.
    def calculate_center_indices_of_platform_block(self):
        """Compute the relative indices of PRINCIPAL_BLOCKs that we need to
        remove from the center of a PLATFORM_BLOCK in order to have enough
        space to insert a pig."""
        self.CENTER_INDICES_OF_PLATFORM_BLOCK = []
        NUMBER_OF_PRINCIPAL_BLOCKS_COVERED_BY_PLATFORM_BLOCK = int(BLOCK_REGISTRY[self.PLATFORM_BLOCK].width / BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].width) + 1 + 1 if BLOCK_REGISTRY[self.PLATFORM_BLOCK].width % BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].width != 0 else 0
        CENTER = int(NUMBER_OF_PRINCIPAL_BLOCKS_COVERED_BY_PLATFORM_BLOCK / 2)
        for index in range(int(BLOCK_REGISTRY['pig'].width / BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].width) + 1):
            half_of_index = int(index / 2)
            if index % 2 == 0:
                self.CENTER_INDICES_OF_PLATFORM_BLOCK.append(CENTER + half_of_index)
            else:
                self.CENTER_INDICES_OF_PLATFORM_BLOCK.append(CENTER - half_of_index - 1)


    def generate_platforms(self):
        return range(self.SHORTEST_COLUMN_HEIGHT)[::int(BLOCK_REGISTRY['pig'].height / BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].height) + 1 + 1 if BLOCK_REGISTRY['pig'].height % BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].height != 0 else 0]


    def insert_platforms(self, platforms):
        for platform in platforms:
            for column in self.blocks:
                column[platform] = 'platform'


    def get_platform_block_start_distance(self, index):
        """
        Get X distance for the start point of the platform block at the given index.
        """
        return -(self.BLOCKS_PER_PLATFORM * BLOCK_REGISTRY[self.PLATFORM_BLOCK].width - self.STRUCTURE_WIDTH) / 2 + index * BLOCK_REGISTRY[self.PLATFORM_BLOCK].width


    def get_column_indices_for_gaps(self):
        failed_attempts = 0
        columns = []
        # FIXME Refactor the magic number "3" below into a constant or
        # expression.
        while failed_attempts < 3:
            platform_block_index = randrange(1, self.BLOCKS_PER_PLATFORM - 1)
            column = int(self.get_platform_block_start_distance(platform_block_index) / BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].width)
            if column not in columns:
                columns.append(column)
            else:
                failed_attempts += 1
        return columns

    # Not being used right now, but might be used in the future.
    def insert_gaps_until_top(self, columns):
        for column in columns:
            for center in self.CENTER_INDICES_OF_PLATFORM_BLOCK:
                for row in range(len(self.blocks[column + center])):
                    if self.blocks[column + center][row] != 'platform':
                        self.blocks[column + center][row] = 'none'


    def insert_gaps_until_top_platform(self, columns):
        for column in columns:
            for row in range(self.platforms[-1]):
                if self.blocks[column][row] != 'platform':
                    for center in self.CENTER_INDICES_OF_PLATFORM_BLOCK:
                        self.blocks[column + center][row] = 'none'


    def get_height_of_block(self, row):
        """
        Assumes the "platforms" are sorted and the blocks in "platforms" have
        been placed in "blocks".
        """
        number_of_platforms = bisect_left(self.platforms, row)
        return GROUND_HEIGHT + (row - number_of_platforms) * BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].height + number_of_platforms * BLOCK_REGISTRY[self.PLATFORM_BLOCK].height


    def get_xml_elements_for_principal_blocks(self):
        """
        Returns XML elements to generate a Science Birds level.
        """
        elements = ''
        for column_index, column in enumerate(self.blocks):
            for block_index, block in enumerate(column):
                if block not in ['platform', 'none']:
                    elements += BLOCK_STRING.format(BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].xml_element_name,
                                                    get_block_type(block),
                                                    column_index * BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].width + BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].width / 2,
                                                    self.get_height_of_block(block_index) + BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].height / 2,
                                                    0)
        return elements


    def get_xml_elements_for_platform_blocks(self):
        elements = ''
        for platform in self.platforms:
            for index in range(self.BLOCKS_PER_PLATFORM):
                elements += BLOCK_STRING.format(BLOCK_REGISTRY[self.PLATFORM_BLOCK].xml_element_name,
                                                'stone',
                                                self.get_platform_block_start_distance(index) + BLOCK_REGISTRY[self.PLATFORM_BLOCK].width / 2,
                                                self.get_height_of_block(platform) + BLOCK_REGISTRY[self.PLATFORM_BLOCK].height / 2,
                                                0)
        return elements


    def construct_level(self):
        self.insert_gaps_until_top_platform(self.get_column_indices_for_gaps())
        principal_block_elements = self.get_xml_elements_for_principal_blocks()
        platform_block_elements = self.get_xml_elements_for_platform_blocks()
        with open(self.LEVEL_PATH, 'w') as level_file:
            level_file.write(LEVEL_TEMPLATE.strip().format(principal_block_elements + platform_block_elements))


if __name__ == '__main__':
    TEST_BLOCKS = [
        ['stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square'],
        ['platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform'],
        ['stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square'],
        ['platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform',     'platform'],
        ['stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square', 'stone_square']
    ]
    Structure(TEST_BLOCKS, [1, 3]).construct_level()
