from lxml import html
from lxml.html import tostring as html2str
import requests
import urllib.request
from urllib.parse import urlparse
import os
import sys
from os.path import splitext
from pprint import pprint
import json
from icecream import ic

def isBlank (myString):
    if myString and myString.strip():
        #myString is not None AND myString is not empty or blank
        return False
    #myString is None OR myString is empty or blank
    return True

details = {}

type_of_import = 'details' # images, details, all

# unset and add new clusters
_sets = {
    # Saga Cluster
    #50, # Saga Cluster 1st 「The Epic of the Dragon Lord
    #51, # Saga Cluster 2nd 「The Magic Stone War - Zero」
    #52, # Saga Cluster 2.5 「Rebirth of Legend」
    #53, # Saga Cluster 3rd 「Assault into the Demonic World 」

    # ALICE ORIGIN

    #42, # Alice Origin 1st Booster Pack
    #43, # Alice Origin 1st Start Deck
    #44, # Alice Origin 2nd Booster Pack
    #45, # Alice Origin 2nd Start Deck
    #46, # Alice Origin 3rd Booster Pack
    #47, # GHOST IN THE SHELL SAC_2045 Starter Deck
    #48, # GHOST IN THE SHELL SAC_2045 Booster Pack
    #49, # Alice Origin 4th Booster Pack

    # New Valhalla Cluster

    #38, # Starter Deck
    #37, # New Dawn Rises
    #39, # The Strangers of New Valhalla
    #40, # Awakening of the Ancients
    #41, # The Decisive Battle of Valhalla

    # Reiya Cluster

    #29, # Starter Deck
    #30, # Ancient Nights
    #31, # Advent of the Demon King
    #33, # Constructed Deck "The Lost Tomes"
    #34, # The Time Spinning Witch
    #35, # Winds of the Ominous Moon

    # Lapis Cluster

    #03, # Starter Deck
    #02, # Curse of the Frozen Casket
    #04, # Legacy Lost
    #26, # Return of the Dragon Emperor
    #28, # Echoes of the New World
    #06, # Vingolf "Ruler All Stars"

    # Alice Cluster

    #07, # Starter Deck "Faria, the Sacred Queen and Melgis, the Flame King"
    #08, # The Seven Kings of the Lands
    #09, # The Twilight Wanderer
    #13, # The Moonlit Savior
    #14, # Battle for Attractia
    #15, # Vingolf "Valkyria Chronicles"

    # Grimm Cluster

    #11, # Crimson Moon'sFairy Tale
    #16, # The Castle of Heaven and The Two Towers
    #17, # The Moon Priestess Returns
    #18, # The Millennia of Ages
    #19, # Vingolf "Engage Knights"
}

_test = {"\n": ""}
_replaces = {
    "costs": {
        "W": "[L]",
        "R": "[F]",
        "B": "[Wa]",
        "G": "[Wi]",
        "D": "[D]",
        "X": "[X]",
        "0": "[0]",
        "1": "[1]",
        "2": "[2]",
        "3": "[3]",
        "4": "[4]",
        "5": "[5]",
        "6": "[6]",
        "7": "[7]",
        "8": "[8]",
        "9": "[9]"
    },
    "text": {
        "\uFF3B": "[",
        "\uFF3D": "]",
        "\u21d2": "=>",
        "\uff0b": "+",
        "\u300a": "<<",
        "\u300b": ">>",
        "Activate ": "[Activate] ",
        "Automatic ": "[Automatic] ",
        "[W]": "[L]",
        "[R]": "[F]",
        "[U]": "[Wa]",
        "[G]": "[Wi]",
        "[B]": "[D]",
        "[w]": "[L]",
        "[r]": "[F]",
        "[u]": "[Wa]",
        "[g]": "[Wi]",
        "[b]": "[D]"
    }
}

URL = 'http://www.fowtcg.com/card/'

cards = []

_ruler = False
cache = open('./cache.json', 'r')
#details = json.loads(cache.read())
details = {}

for set in _sets:
    page = 1
    for page in range(1, 6):
        process = '{}?s={}&page={}'.format('http://www.fowtcg.com/cards/',set,page)
        _page = requests.get(process)
        tree = html.fromstring(_page.content)
        for entry in tree.xpath('//div[@class="search-result-detail col-xs-10"]//a/@href'):
            if len(entry) > 0:
                ic(entry.split('/')[2])
                cards.append(entry.split('/')[2])

for url_range in cards:
    cached = False
    for i in details.values():
        if url_range == i['page']:
            print("[Success] Found ",i['Name']," in cache.")
            cached = True
            continue
    if cached:
        continue
    page = requests.get(URL+str(url_range))
    tree = html.fromstring(page.content)

    name = ''.join(tree.xpath('//h2[@class="line-heading line-heading-gradient line-heading-large"]/text()'))
    image = ''.join(tree.xpath('//div[@class="ps-gallery"]//a/@href'))

    if not isBlank(name):
        #details[int(url_range)] = []
        detail = {}
        detail['Name'] = name
        detail['Image'] = image
        detail['page'] = url_range
        #details[int(START)].append(detail)
        for item in tree.xpath('//div[@class="prop-item col-xs-4"]'):
            #print(item.xpath('./p[@class="prop-label"]/text()'))
            text_option = ''.join(item.xpath('./p[@class="prop-value"]/text()'))
            header_option = ''.join(item.xpath('./p[@class="prop-label"]/text()'))
            if(header_option == 'Race and Trait') and (text_option == ''):
                detail[header_option] = '-'
            elif(header_option == 'ATK/DEF') and (text_option == ''):
                detail[header_option] = '0 / 0'
            elif(header_option == 'Cost'):
                cost = ''
                for costs in item.xpath('./p[@class="prop-value"]//img'):
                    cost = cost+''.join(costs.xpath('.//@alt'))
                #ic(cost)
                cost = ''.join([_test.get(c, c) for c in cost])
                cost = ''.join([_replaces['costs'].get(c, c) for c in cost])
                #ic(cost)
                detail[header_option] = cost
            else:
                text_option = ''.join([_test.get(c, c) for c in text_option])
                text_option = ''.join([_replaces['text'].get(c, c) for c in text_option])

                detail[header_option] = text_option
            #details[int(START)].append(detail)

        card_text = []
        for item2 in tree.xpath('//section[@class="mgtp30px"]'):
            i = item2.xpath('.//*[self::h3]/text()')
            t = []
            for item3 in item2.xpath('.//section'):
                for x in range(0,len(item3)):
                    if item3[x].tag == 'p':
                        _temp = item3[x].text
                        _temp = ''.join([_test.get(c,c) for c in _temp])
                        #ic(_temp)
                        #ic(len(_temp))
                        t.append(_temp)
            #t = item2.xpath('.//*[self::p]/text()')
            #ic(t)
            detail[''.join(item2.xpath('.//*[self::h3]/text()'))] = ''.join(t)
        try:
            t_cost = 0
            attibutes = []
            for symbol in ['[L]','[F]','[Wa]','[Wi]','[D]']:
                if symbol in detail['Cost']:
                    t_cost = t_cost+len(symbol)
            for symbol2 in ['[0]','[1]','[2]','[3]','[4]','[5]']:
                if symbol2 in detail['Cost']:
                    t_cost = int(symbol2.replace('[','').replace(']',''))*len(symbol2)
            if '[L]' in detail['Cost']:
                attibutes.append('Light')
            elif '[F]' in detail['Cost']:
                attibutes.append('Fire')
            elif '[Wa]' in detail['Cost']:
                attibutes.append('Water')
            elif '[Wi]' in detail['Cost']:
                attibutes.append('Wind')
            elif '[D]' in detail['Cost']:
                attibutes.append('Darkness')
            detail['Total Cost'] = t_cost
            detail['Attribute'] = '/'.join(attibutes)
        except:
            print(end="")
        # check our data
        checks = [
            'Card Number',
            'Rarity',
            'Cost',
            'ATK/DEF',
            'Type',
            'Race and Trait',
            'Illust',
            'Card Text',
            'Flavor Text',
            'Total Cost',
            'Attribute'
        ]
        for i in checks:
            if i not in detail:
                detail[i] = "[ERROR] PLEASE CHECK ME."


        #details[int(url_range)].append(detail)
        #details[detail['Card Number']] = {}
        details[detail['Card Number']] = detail
        with open('./cache.json', 'w') as filetowrite:
            filetowrite.write(json.dumps(details, indent=4))
        print("[Success] Found data for",url_range,"as [",detail['Card Number'],'][',detail['Name'],"]")
    else:
        print("[Error] Skipping ",url_range," since name was blank.")

f1 = open('./temp.tsv','w')
f2 = open('./cardurls.txt', 'w')

ruler_data = {
    "Name": "",
    "Set": "",
    "ImageFile": "",
    "SetID": "",
    "Type": "",
    "Subtype": "",
    "Cost": "",
    "TCost": "",
    "ATK": "",
    "DEF": "",
    "Attribute": "",
    "Rarity": "",
    "Cardtext": "",
    "Script": ""
}

for items in sorted(details):
    if items in details:
        item = details[items]
        if item['Card Number'] in ['Buy a Box']:
            pass
        #print('Parsing '+str(items))
        if(type_of_import == 'test'):
            for i,j in item.items():
                print('{}: {}'.format(repr(i),repr(j)))
            print()
        if(type_of_import == 'all') or (type_of_import == 'details'):
            #pprint(item)
            #print(item['Type'])
            #if(item['Type'] != 'Ruler') or (item['Type'] != 'J-Ruler'):
            try:
                if(item['Type'] == 'Ruler'):
                    ruler_data['Name'] = item['Name'].replace('\u3010','[').replace('\u3011','] ') # Name
                    ruler_data['Set'] = item['Card Number'].split('-')[0] # Set
                    ruler_data['ImageFile'] = item['Card Number'] # ImageFile
                    ruler_data['SetID'] = item['Card Number'] # SetID
                    ruler_data['Type'] = item['Type'] # Type
                    ruler_data['Subtype'] = item['Race and Trait'] # Subtype/Race
                    ruler_data['Cost'] = item['Cost'] # Cost
                    ruler_data['TCost'] = item['Total Cost'] # T.Cost
                    ruler_data['ATK'] = '0' # ATK
                    ruler_data['DEF'] = '0' # DEF
                    ruler_data['Attribute'] = item['Attribute'] # Attribute
                    ruler_data['Rarity'] = item['Rarity'] # Rarity
                    ruler_data['Illust'] = item['Illust']
                    ruler_data['FlavorText'] = item['Flavor Text']
                    item['Card Text'] = ''.join([_replaces['text'].get(c,c) for c in item['Card Text']])
                    ruler_data['Cardtext'] = item['Card Text'] # Cardtext
                    ruler_data['Script'] = ''                                     # Script
                    #print(ruler_data)
                elif(item['Type'] == 'J-Ruler'): # "{} | {}".format(ruler_data[''],
                    print("J-Ruler")
                    print("{} | {}".format(ruler_data['Name'],item['Name'].replace('\u3010','[').replace('\u3011','] ')),end='\t',file=f1)                        # Name
                    print(item['Card Number'].split('-')[0],end='\t',file=f1)   # Set
                    print("{},{}".format(ruler_data['ImageFile'],item['Card Number']),end='\t',file=f1)                 # ImageFile
                    print(item['Card Number'],end='\t',file=f1)                 # SetID
                    print("{} | {}".format(ruler_data['Type'],item['Type']),end='\t',file=f1)                        # Type
                    print(item['Race and Trait'],end='\t',file=f1)              # Subtype/Race
                    print(item['Cost'],end='\t',file=f1)                        # Cost
                    print(item['Total Cost'],end='\t',file=f1)                  # T.Cost
                    print("{} | {}".format(ruler_data['ATK'],item['ATK/DEF'].split(' / ')[0]),end='\t',file=f1)     # ATK
                    print("{} | {}".format(ruler_data['DEF'],item['ATK/DEF'].split(' / ')[1]),end='\t',file=f1)     # DEF
                    print("{} | {}".format(ruler_data['Attribute'],item['Attribute']),end='\t',file=f1)                                  # Attribute
                    print("JR",end='\t',file=f1)                      # Rarity
                    print(item['Illust'],end='\t',file=f1)
                    print("{} | {}".format(ruler_data['FlavorText'],item['Flavor Text']),end="\t",file=f1)
                    for _i in _replaces['text']:
                        item['Card Text'] = item['Card Text'].replace(_i['_orig'], _i['_new'])
                    print("{} | {}".format(ruler_data['Cardtext'],item['Card Text']),end='\t',file=f1)                   # Cardtext
                    print('',end='\t',file=f1)                                         # Script
                    ruler_data.clear()
                else:
                    print(item['Name'].replace('\u3010','[').replace('\u3011','] '),end='\t',file=f1)                        # Name
                    print(item['Card Number'].split('-')[0],end='\t',file=f1)   # Set
                    print(item['Card Number'],end='\t',file=f1)                 # ImageFile
                    print(item['Card Number'],end='\t',file=f1)                 # SetID
                    print(item['Type'],end='\t',file=f1)                        # Type
                    print(item['Race and Trait'],end='\t',file=f1)              # Subtype/Race
                    print(item['Cost'],end='\t',file=f1)                        # Cost
                    print(item['Total Cost'],end='\t',file=f1)                  # T.Cost
                    if ' / ' in item['ATK/DEF']:
                        print(item['ATK/DEF'].split(' / ')[0],end='\t',file=f1) # ATK
                        print(item['ATK/DEF'].split(' / ')[1],end='\t',file=f1) # DEF
                    else:
                        print('',end='\t',file=f1)                              # ATK
                        print('',end='\t',file=f1)                              # DEF
                    print(item['Attribute'],end='\t',file=f1)                   # Attribute
                    print(item['Rarity'],end='\t',file=f1)                      # Rarity
                    print(item['Illust'],end='\t',file=f1)                      # Illust
                    print(item['Flavor Text'],end='\t',file=f1)                      # Flavor Text
                    item['Card Text'] = ''.join([_replaces['text'].get(c,c) for c in item['Card Text']])
                    print(item['Card Text'],end='\t',file=f1)                   # Cardtext
                    print('',file=f1)                                           # Script
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("[Error] ",e,exc_type, fname, exc_tb.tb_lineno)
                #pprint(item)
                '''
                print(' ',end='\t',file=f1)                     # Name
                print(' ',end='\t',file=f1)                     # Set
                print(' ',end='\t',file=f1)                     # ImageFile
                print(' ',end='\t',file=f1)                     # SetID
                print(' ',end='\t',file=f1)                     # Type
                print(' ',end='\t',file=f1)                     # Subtype/Race
                print(' ',end='\t',file=f1)                     # Cost
                print(' ',end='\t',file=f1)                     # T.Cost
                print(' ',end='\t',file=f1)                     # ATK
                print(' ',end='\t',file=f1)                     # DEF
                print(' ',end='\t',file=f1)                     # Attribute
                print(' ',end='\t',file=f1)                     # Rarity
                print(' ',end='\t',file=f1)                     # Cardtext
                print(' ',file=f1)                              # Script
                '''
        if(type_of_import == 'images') or (type_of_import == 'all'):
            try:
                os.makedirs(item['Card Number'].split('-')[0],exist_ok=True)
                os.makedirs(item['Card Number'].split('-')[0]+'/low',exist_ok=True)
                path = urlparse(item['Image']).path
                ext = splitext(path)[1]
                location = ''.join(item['Card Number'].split('-')[0])+'/low/'+''.join(item['Card Number'].replace('*','-fix'))+ext
                if not os.path.exists(location):
                    urllib.request.urlretrieve(item['Image'], location)
            except:
                print("Opps We got an error with an image")
        if(type_of_import == 'details') or (type_of_import == 'all'):
                print("{}/{}.jpg".format(item['Card Number'].split('-')[0],item['Card Number']),end='\t',file=f2)
                print(item['Image'],file=f2)
    else:
        print('[Error for {}]'.format(items),end='\t',file=f1)  # Name
        print('',end='\t',file=f1)                              # Set
        print('',end='\t',file=f1)                              # ImageFile
        print('',end='\t',file=f1)                              # SetID
        print('',end='\t',file=f1)                              # Type
        print('',end='\t',file=f1)                              # Subtype/Race
        print('',end='\t',file=f1)                              # Cost
        print('',end='\t',file=f1)                              # T.Cost
        print('',end='\t',file=f1)                              # ATK
        print('',end='\t',file=f1)                              # DEF
        print('',end='\t',file=f1)                              # Attribute
        print('',end='\t',file=f1)                              # Rarity
        print('',end='\t',file=f1)                              # Illust
        print('',end='\t',file=f1)                              # Flavor Text
        print('',end='\t',file=f1)                              # Cardtext
        print('',file=f1)                                       # Script
