import requests
import re
import json
import argparse


def get_html(url:str) -> str:
    print('Fetching HTML...')
    html = requests.get(url).text.replace('\n', '').replace('\t', '')
    while '  ' in html:
        html = html.replace('  ', ' ')
    print('Fetched HTML!')
    return html

def get_links(page_html:str) -> list:  
    print('Collecting links from page...')
    sub1 = '<nav class="page-nav"> <ul>'
    sub2 = '</ul> </nav>'
    start = str(re.escape(sub1))
    end = str(re.escape(sub2))
 
    res = re.findall(start + '(.*)' + end, page_html)[0]
    res = res.split('</li>')
    # print(res)

    pages = []
    for item in res:
        if item == ' ': continue
        isub1 = '<li'
        isub2 = '</div> <a'

        istart = str(re.escape(isub1))
        iend = str(re.escape(isub2))

        filler_list = re.findall(istart + '(.*)' + iend, item)
        if len(filler_list) < 1: continue
        filler = re.findall(istart + '(.*)' + iend, item)[0]

        item = item.replace(isub1 + filler + isub2, '').strip()
        item = item.replace('</a>', '')
        item = item.replace('href=', '')
        item = item.replace('"', '')

        item = item.split('>')
        slug = item[0].split('/')[-1]

        pages.append({'href': item[0], 'slug': slug, 'name': item[1]})
    print('Links collected!')
    return pages


def get_config(links:list, default:str) -> dict:
    print('Generating config...')
    config = {
        'templates': {
            'kaart': {
                "name": "Kaart",
                "href": default,
            },
        },
        'pages': [],
        'base_url':  default.split('/')[0] + '//' + default.split('/')[2]
    }

    for link in links:
        idx = links.index(link)
        btns = []
        if idx == 0:
            btns = [{
                'name': 'Start',
                'href': links[idx+1]['href'],
            }]
        elif idx == 1:
            btns = [
                'templates.kaart',
                {
                    'name': 'Volgende',
                    'href': links[idx+1]['href'],
                },
            ]
        elif idx == len(links) - 1:
            btns = [
                {
                    'name': 'Vorige',
                    'href': links[idx-1]['href'],
                },
                'templates.kaart',
            ]
        else:
            btns = [
                {
                    'name': 'Vorige',
                    'href': links[idx-1]['href'],
                },
                'templates.kaart',
                {
                    'name': 'Volgende',
                    'href': links[idx+1]['href'],
                },
            ]

        config['pages'].append({
                'slug': link['slug'],
                'buttons': btns,
            })
    
    print('Generated config!')
    return config

def generate_config(url:str) -> dict:
    return get_config(get_links(get_html(url)), url)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Routekaart Button Config Generator', description='Generate the config for the Routekaart buttons from a webpage')
    parser.add_argument('address')
    parser.add_argument('-o', '--output')
    parser.add_argument('-d', '--default')

    args = parser.parse_args()

    # html = get_html(args.address)
    # links = get_links(html)
    # config = get_config(links, args.address)

    config = generate_config(args.address)

    if args.output:
        OUTPUT = args.output
    else:
        print('No output specified, using "config.json"')
        if input('Do you want to procceed? [Y/N] ').upper() != 'Y':
            exit()
        OUTPUT = 'config.json'
    
    with open(OUTPUT, 'w') as of:
        json.dump(config, of)