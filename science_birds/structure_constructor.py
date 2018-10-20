import logging as log
from bisect import bisect_left

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
        self.BLOCKS = remove_ice_blocks(transpose_and_invert_blocks(blocks))
        self.STRUCTURE_WIDTH = BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].width * len(self.BLOCKS)
        self.BLOCKS_PER_PLATFORM = int(self.STRUCTURE_WIDTH / BLOCK_REGISTRY[self.PLATFORM_BLOCK].width) + 1
        self.SHORTEST_COLUMN_HEIGHT = len(min(self.BLOCKS, key=len))
        if platforms is None:
            platforms = self.generate_platforms()
            self.insert_platforms(platforms)
        self.platforms = platforms


    def generate_platforms(self):
        return range(self.SHORTEST_COLUMN_HEIGHT)[::int(BLOCK_REGISTRY['pig'].height / BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].height) + 1 + 1 if BLOCK_REGISTRY['pig'].height % BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].height != 0 else 0]


    def insert_platforms(self, platforms):
        for platform in platforms:
            for column in self.BLOCKS:
                column[platform] = 'platform'


    def get_platform_block_start_distance(self, index):
        """
        Get X distance for the start point of the platform block at the given index.
        """
        return -(self.BLOCKS_PER_PLATFORM * BLOCK_REGISTRY[self.PLATFORM_BLOCK].width - self.STRUCTURE_WIDTH) / 2 + index * BLOCK_REGISTRY[self.PLATFORM_BLOCK].width


    def get_column_indices_for_gaps(self):
        """Get column indices to make room to place a pig in the center of each
        platform block, except the platform blocks on edges."""
        columns = []
        previous_platform_block_start_distance = self.get_platform_block_start_distance(0)
        for platform_block_index in range(1, self.BLOCKS_PER_PLATFORM - 1):
            platform_block_start_distance = previous_platform_block_start_distance + BLOCK_REGISTRY[self.PLATFORM_BLOCK].width
            primary_block_index_for_platform_block_start = platform_block_start_distance / BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].width
            platform_block_end_distance = platform_block_start_distance + BLOCK_REGISTRY[self.PLATFORM_BLOCK].width
            primary_block_index_for_platform_block_end = platform_block_end_distance / BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].width
            primary_block_index_for_platform_block_center = int((primary_block_index_for_platform_block_start + primary_block_index_for_platform_block_end) / 2)
            columns.append(primary_block_index_for_platform_block_center)
            previous_platform_block_start_distance = platform_block_start_distance
        principal_blocks_per_pig, remainder_distance = divmod(BLOCK_REGISTRY['pig'].width, BLOCK_REGISTRY[self.PRINCIPAL_BLOCK].width)
        principal_blocks_per_pig = int(principal_blocks_per_pig)
        if remainder_distance != 0:
            principal_blocks_per_pig += 1
        center_offsets = [i / 2 if i % 2 == 0 else -(i / 2 + 1) for i in range(principal_blocks_per_pig)]
        return [column + center_offset for column in columns for center_offset in center_offsets]


    # Not being used right now, but might be used in the future.
    def insert_gaps_until_top(self, columns):
        for column in columns:
            for row in range(len(self.BLOCKS[column])):
                if self.BLOCKS[column][row] != 'platform':
                    self.BLOCKS[column][row] = 'none'


    def insert_gaps_until_top_platform(self, columns):
        for column in columns:
            for row in range(self.platforms[-1]):
                if self.BLOCKS[column][row] != 'platform':
                    self.BLOCKS[column][row] = 'none'


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
        for column_index, column in enumerate(self.BLOCKS):
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
