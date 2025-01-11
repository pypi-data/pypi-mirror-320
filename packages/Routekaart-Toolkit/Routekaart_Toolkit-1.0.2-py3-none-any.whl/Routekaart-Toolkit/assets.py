BUTTON_CONTAINER = '''
<figure>
    <style>
        div#route-buttons {
            display: flex;
            justify-content: space-between;
        }

        button.route-navigation {
            background-color: #00904d;
            transition: transform 0.5s;
            cursor: pointer;
        }

        button.route-navigation:hover {
            transform: scale(1.1);
        }
    </style>    
    <div id="route-buttons">
        {{buttons}}
    </div>
</figure>
'''

BUTTON = '''
<a href="{{button_href}}" class="route-navigation">
    <button class="route-navigation">
        {{button_name}}
    </button>
</a>
'''

MAP_TEMPLATE = '''
<figure>
    <style>
        div#container {
            width: 100%;
            position: relative;
            display: grid;
        }

        div#container > * {
            grid-column: 1;
            grid-row: 1;
        }

        img#backdrop {
            width: 100%;
        }
    </style>
    <div id="container">
    <img id="backdrop" src="{{image_url}}" alt="">
{{svg}}
    </div>
</figure>
'''