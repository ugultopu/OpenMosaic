from constants import (BLOCK_REGISTRY,
                       MULTIPLIER,
                       GROUND_HEIGHT,
                       BLOCK_STRING,
                       PIG_STRING,
                       LEVEL_TEMPLATE)


class Structure:
    """ A building-like structure for Science Birds.

    This does not represent a whole Science Birds level. It represents only a
    structure in a Science Birds level.

    Blocks are represented in a matrix (that is, a list of lists). Each row of
    the matrix represents a column of the structure. That is, the matrix
    represents the structure starting from bottom-left and goes towards
    top-right, by going up the column first, then to the next column.
    """

    @staticmethod
    def transpose_and_invert_blocks(blocks):
        """
        The blocks blocks start from top-left and go towards bottom-right. This is
        not practical when constructing a Science Birds level. We want to start
        from bottom-left and go towards top-right. Hence, we transpose and invert
        blocks blocks.
        """
        return [column[::-1] for column in map(list, zip(*blocks))]


    @staticmethod
    def remove_ice_blocks(blocks):
        """
        Since ice blocks usually represent whitespace (i.e, background), we want to
        remove them.
        """
        return [[block for block in column if not block.startswith('ice')] for column in blocks]


    @staticmethod
    def get_number_of_instances_required_to_cover_distance(covered_distance, covering_distance):
        number_of_instances, remainder = divmod(int(covered_distance * MULTIPLIER),
                                                int(covering_distance * MULTIPLIER))
        if remainder:
            number_of_instances += 1
        return number_of_instances


    def __init__(self,
                 level_path,
                 primary_block,
                 auxiliary_block,
                 platform_block,
                 blocks):
        self.LEVEL_PATH = level_path
        self.PRIMARY_BLOCK = primary_block
        """ PRIMARY_BLOCK is the block that is used to fill up the structure
        above the top platform."""
        self.AUXILIARY_BLOCK = auxiliary_block
        """ AUXILIARY_BLOCK is the block that is used to fill up the structure
        below the top platform."""
        self.PLATFORM_BLOCK = platform_block
        self.BLOCKS = self.remove_ice_blocks(self.transpose_and_invert_blocks(blocks))
        self.STRUCTURE_WIDTH = BLOCK_REGISTRY[self.PRIMARY_BLOCK].width * len(self.BLOCKS)
        self.BLOCKS_PER_PLATFORM = self.get_number_of_instances_required_to_cover_distance(self.STRUCTURE_WIDTH,
                                                                                           BLOCK_REGISTRY[self.PLATFORM_BLOCK].width)
        self.NUMBER_OF_PRIMARY_BLOCKS_IN_SHORTEST_COLUMN = len(min(self.BLOCKS, key=len))
        self.BLOCKS_ABOVE_TOP_PLATFORM = [column[self.NUMBER_OF_PRIMARY_BLOCKS_IN_SHORTEST_COLUMN:] for column in self.BLOCKS]
        self.SHORTEST_COLUMN_HEIGHT = self.NUMBER_OF_PRIMARY_BLOCKS_IN_SHORTEST_COLUMN * BLOCK_REGISTRY[self.PRIMARY_BLOCK].height
        self.calculate_lateral_number_of_auxiliary_blocks_per_pig()
        self.calculate_vertical_number_of_auxiliary_blocks_per_pig()
        self.calculate_platform_start_distance()
        self.calculate_gap_indices_of_all_platform_blocks()
        self.calculate_story_height()
        self.calculate_number_of_stories()
        self.calculate_number_of_auxilary_blocks_per_row()


    def calculate_lateral_number_of_auxiliary_blocks_per_pig(self):
        '''Calculate the number of auxiliary blocks on X axis that needs to be
        removed in order to fit one pig. Needs to be called only once.'''
        self.LATERAL_NUMBER_OF_AUXILIARY_BLOCKS_PER_PIG = self.get_number_of_instances_required_to_cover_distance(BLOCK_REGISTRY['pig'].width,
                                                                                                                  BLOCK_REGISTRY[self.AUXILIARY_BLOCK].width)


    def calculate_vertical_number_of_auxiliary_blocks_per_pig(self):
        '''Calculate the number of auxiliary blocks on Y axis that needs to be
        removed in order to fit one pig. Needs to be called only once.'''
        self.VERTICAL_NUMBER_OF_AUXILIARY_BLOCKS_PER_PIG = self.get_number_of_instances_required_to_cover_distance(BLOCK_REGISTRY['pig'].height,
                                                                                                                   BLOCK_REGISTRY[self.AUXILIARY_BLOCK].height)


    def calculate_platform_start_distance(self):
        self.PLATFORM_START_DISTANCE = -(self.BLOCKS_PER_PLATFORM * BLOCK_REGISTRY[self.PLATFORM_BLOCK].width - self.STRUCTURE_WIDTH) / 2


    def get_lateral_distance_of_block(self, column, block_type):
        lateral_distance = column * BLOCK_REGISTRY[block_type].width + BLOCK_REGISTRY[block_type].width / 2
        if block_type is self.PLATFORM_BLOCK:
            # Platforms start a bit before than normal blocks.
            return self.PLATFORM_START_DISTANCE + lateral_distance
        else:
            return lateral_distance


    def get_gap_indices_of_platform_block(self, index):
        '''A platform block rests on auxiliary blocks. We need to calculate the
        center indices of auxiliary blocks to skip inserting auxiliary blocks
        there in order leave room for pigs.'''
        block_center = self.get_lateral_distance_of_block(index, self.PLATFORM_BLOCK)
        start_distance = block_center - BLOCK_REGISTRY[self.PLATFORM_BLOCK].width / 2
        start_index = int(start_distance / BLOCK_REGISTRY[self.AUXILIARY_BLOCK].width)
        end_distance = block_center + BLOCK_REGISTRY[self.PLATFORM_BLOCK].width / 2
        end_index = int(end_distance / BLOCK_REGISTRY[self.AUXILIARY_BLOCK].width)
        center_index, remainder = divmod(start_index + end_index, 2)
        gap_indices = [center_index]
        if remainder:
            gap_indices.append(center_index + 1)
        while len(gap_indices) < self.LATERAL_NUMBER_OF_AUXILIARY_BLOCKS_PER_PIG:
            gap_indices = [gap_indices[0] - 1] + gap_indices + [gap_indices[-1] + 1]
        return gap_indices


    def calculate_gap_indices_of_all_platform_blocks(self):
        self.GAP_INDICES = []
        for platform in range(1, self.BLOCKS_PER_PLATFORM - 1):
            gap_indices = self.get_gap_indices_of_platform_block(platform)
            print 'gap indices for platform "{}" is "{}"'.format(platform, gap_indices)
            self.GAP_INDICES.extend(gap_indices)


    def calculate_story_height(self):
        '''A "story" is the part of the structure starting from the top of the
        closest platform below (or from the ground) and going until the top of
        the closest platform above. This function needs to be called only once,
        since every story has the same height.'''
        self.STORY_HEIGHT = self.VERTICAL_NUMBER_OF_AUXILIARY_BLOCKS_PER_PIG * BLOCK_REGISTRY[self.AUXILIARY_BLOCK].height + BLOCK_REGISTRY[self.PLATFORM_BLOCK].height


    def calculate_number_of_stories(self):
        self.NUMBER_OF_STORIES = self.get_number_of_instances_required_to_cover_distance(self.SHORTEST_COLUMN_HEIGHT,
                                                                                         self.STORY_HEIGHT)


    def calculate_number_of_auxilary_blocks_per_row(self):
        self.AUXILIARY_BLOCKS_PER_ROW = self.get_number_of_instances_required_to_cover_distance(self.STRUCTURE_WIDTH,
                                                                                                BLOCK_REGISTRY[self.AUXILIARY_BLOCK].width)


    def get_xml_elements_for_auxiliary_blocks(self):
        elements = ''
        for story in range(self.NUMBER_OF_STORIES):
            for column in range(self.AUXILIARY_BLOCKS_PER_ROW):
                if column not in self.GAP_INDICES:
                    for block in range(self.VERTICAL_NUMBER_OF_AUXILIARY_BLOCKS_PER_PIG):
                        elements += BLOCK_STRING.format(BLOCK_REGISTRY[self.AUXILIARY_BLOCK].xml_element_name,
                                                        'stone',
                                                        self.get_lateral_distance_of_block(column, self.AUXILIARY_BLOCK),
                                                        GROUND_HEIGHT + story * self.STORY_HEIGHT + block * BLOCK_REGISTRY[self.AUXILIARY_BLOCK].height + BLOCK_REGISTRY[self.AUXILIARY_BLOCK].height / 2,
                                                        0)
        return elements


    def get_xml_elements_for_platforms(self):
        elements = ''
        for story in range(self.NUMBER_OF_STORIES):
            for block_order in range(self.BLOCKS_PER_PLATFORM):
                elements += BLOCK_STRING.format(BLOCK_REGISTRY[self.PLATFORM_BLOCK].xml_element_name,
                                                'stone',
                                                self.get_lateral_distance_of_block(block_order, self.PLATFORM_BLOCK),
                                                GROUND_HEIGHT + (story + 1) * self.STORY_HEIGHT - BLOCK_REGISTRY[self.PLATFORM_BLOCK].height / 2,
                                                0)
        return elements


    def construct_level(self):
        with open(self.LEVEL_PATH, 'w') as level_file:
            level_file.write(LEVEL_TEMPLATE.strip().format(self.get_xml_elements_for_auxiliary_blocks()
                                                           + self.get_xml_elements_for_platforms()))
