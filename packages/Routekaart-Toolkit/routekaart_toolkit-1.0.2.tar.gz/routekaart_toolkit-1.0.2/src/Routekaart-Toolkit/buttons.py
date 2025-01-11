import json
import argparse

from .utility import create_empty_folder
from .assets import BUTTON_CONTAINER, BUTTON
from .config import generate_config


def generate_button(button:dict) -> str:
    temp = BUTTON
    temp = temp.replace('{{button_href}}', button['href'])
    temp = temp.replace('{{button_name}}', button['name'])
    print('    Generated button', button['name'], '!')
    return temp
    

def generate_button_set(button_set:dict, templates) -> set:
    print('  Generating button set for', button_set['slug'] + '...')
    buttons = []
    for button in button_set['buttons']:
        if type(button) is str:
            button = button.split('.')[1]
            button = templates[button]
            buttons.append(generate_button(button))
        else:
            buttons.append(generate_button(button))
    container_content = '\n'.join(buttons)
    template = BUTTON_CONTAINER
    template = template.replace('{{buttons}}', container_content)

    if len(buttons) == 1:
        template = template.replace('space-between', 'center') 

    return template
    

def generate_button_sets(config:dict) -> list:
    print('Generating buttons sets...')
    button_sets = [
        {
            'slug': page['slug'],
            'html': generate_button_set(page, config['templates'])
        } 
        for page in config['pages']
    ]
    print('Generated all button sets!')
    return button_sets
      
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Routekaart Button Generator', description='Generate buttons for the Routekaart')
    parser.add_argument('config')
    parser.add_argument('-o', '--output')

    args = parser.parse_args()

    if '.json' in args.config:
        with open(args.config) as output:
            config = json.load(output)
    elif 'http' in args.config:
        config = generate_config(args.config)


    sets = generate_button_sets(config)
    if args.output:
        OUTPUT = args.output
    else:
        print('No output specified, using "buttons"')
        if input('Do you want to procceed? [Y/N] ').upper() != 'Y':
            exit()
        OUTPUT = 'buttons'

    create_empty_folder(OUTPUT)

    for button_set in sets:
        with open(OUTPUT + '/' + button_set['slug'] + '.html', 'w') as of:
            of.write(button_set['html'])