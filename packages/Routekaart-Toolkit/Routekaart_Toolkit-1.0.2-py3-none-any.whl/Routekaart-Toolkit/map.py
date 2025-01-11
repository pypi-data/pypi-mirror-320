import argparse
import json

from .assets import MAP_TEMPLATE


def add_links(svg:str, config:dict) -> str:
    print('Adding links to map...')
    pages = config['pages'].copy()
    pages.pop(0)
    for page in pages:
        idx = pages.index(page)
        svg = svg.replace('{{link:' + str(idx + 1) + '}}', config['base_url'] + '/' + page['slug'])
        print('  Added link', idx)
    print('Added all links!')
    return svg


def generate_map(svg:str, image:str) -> str:
    print('Filling map template...')
    filled = MAP_TEMPLATE.replace('{{svg}}', svg)
    filled = filled.replace('{{image_url}}', image)
    print('Filled map template!')
    return filled


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Routekaart Map Generator', description='Generate the Map for the Routekaart')
    parser.add_argument('svg_file')
    parser.add_argument('image_url')
    parser.add_argument('-c', '--config')
    parser.add_argument('-o', '--output')

    args = parser.parse_args()

    if args.output:
        OUTPUT = args.output
    else:
        print('No output specified, using "map.html"')
        if input('Do you want to procceed? [Y/N] ').upper() != 'Y':
            exit()
        OUTPUT = 'map.html'

    with open(args.svg_file) as svg:
        content = svg.read()
        if args.config:
            with open(args.config) as cnfg:
                config = json.load(cnfg)
                content = add_links(content, config)
        with open(OUTPUT, 'w') as of:
            of.write(generate_map(content, args.image_url))