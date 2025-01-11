import argparse

from .config import generate_config
from .map import add_links, generate_map
from .buttons import generate_button_sets
from .utility import create_empty_folder, proceedConfirmation


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Routekaart Generator',
        description='Generate everything with one handy tool!',
    )

    parser.add_argument('-a', '--address')
    parser.add_argument('-v', '--vector')
    parser.add_argument('-i', '--image')
    parser.add_argument('-o', '--output')
    parser.add_argument('-f', '--force', action='store_true')

    args = parser.parse_args()

    print('Generating all files...')


    if not args.address:
        ADDRESS = input('Enter full url of the main page (with the map): ')
    else:
        ADDRESS = args.address
    
    if not args.vector:
        VECTOR = input('Enter path of the SVG file: ')
    else:
        VECTOR = args.vector

    if not args.image:
        IMAGE = input('Enter full url of the image (for the map): ')
    else:
        IMAGE = args.image

    print('')

    print('Using following parameters:')
    print('  Page URL:', ADDRESS)
    print('  SVG File:', VECTOR)
    print('  IMAGE URL:', IMAGE)
    proceedConfirmation(args.force)

    print('')


    if args.output:
        OUTPUT = args.output
    else:
        print('No output specified, using "Routekaart-Output"')
        proceedConfirmation(args.force)
        OUTPUT = 'Routekaart-Output'
    OUTPUT_BUTTON = OUTPUT + '/buttons'


    with open(VECTOR) as svg_in:
        FILE_SVG = svg_in.read()

    config = generate_config(ADDRESS)
    print('')
    map = generate_map(add_links(FILE_SVG, config), IMAGE)
    print('')
    buttons = generate_button_sets(config)

    print('')

    create_empty_folder(OUTPUT)
    create_empty_folder(OUTPUT_BUTTON)
    print('Made output folders!')

    print('')

    with open(OUTPUT + '/Routekaart.html', 'w') as map_out:
        map_out.write(map)
        print('Map file created!')
    
    print('')
    
    print('Creating button files...')
    for button in buttons:
        with open(OUTPUT_BUTTON + '/' + button['slug'] + '.html', 'w') as of:
            of.write(button['html'])
            print('  Created', button['slug'], 'file!')