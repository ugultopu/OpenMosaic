BLOCK_REGISTRY = {
    'square_with_hole': {
        'xml_name': 'SquareHole',
        'width': 0.85,
        'height': 0.85
    },
    'tiny_square': {
        'xml_name': 'SquareTiny',
        'width': 0.22,
        'height': 0.22
    },
    'long_rectangle': {
        'xml_name': 'RectBig',
        'width': 2.06,
        'height': 0.22
    },
    'pig': {
        'xml_name': 'BasicSmall',
        'width': 0.5,
        'height': 0.5
    }
}

GROUND_HEIGHT = -3.5

BLOCK_STRING = '<Block type="{}" material="{}" x="{}" y="{}" rotation="{}"/>\n'
PIG_STRING = '<Pig type="{}" material="{}" x="{}" y="{}" rotation="{}"/>\n'

# WARNING Science Birds is _very_ picky about its XML. For example, the game
# breaks (the level selection buttons are not rendered in level selection menu)
# if the leading newline in the level template is not trimmed. The same
# peculiarity happens if a <Block> elements start on the same line as the
# <GameObject> element.
LEVEL_TEMPLATE ='''
<?xml version="1.0" encoding="utf-16"?>
<Level width="2">
  <Camera x="0" y="2" minWidth="20" maxWidth="30">
    <Birds>
      <Bird type="BirdRed"/>
    </Birds>
    <Slingshot x="-8" y="-2.5">
      <GameObjects>
        {}
      </GameObjects>
    </Slingshot>
  </Camera>
</Level>
'''
