import xlrd
import re

loc = "Document #1 (Before).xlsx"
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

items = []
for row in range(1, sheet.nrows):
    index=row
    name = sheet.cell_value(row, 0)
    desc = sheet.cell_value(row, 1)
    qty2 = sheet.cell_value(row, 2)
    units2 = sheet.cell_value(row, 3)
    qty1 = sheet.cell_value(row, 4)
    units1 = sheet.cell_value(row, 5)
    item = {
        'name': name, 
        'desc': desc, 
        'qty2': qty2,
        'units2': units2, 
        'qty1': qty1, 
        'units1': units1, 
        'index':row, 
        'matched':False,
        'floor': None,
        'section':None,
        'type': None
    }
    items.append(item)


def checkInt(x):
    try:
        int(x)
        return True
    except ValueError:
        return False


def getMaterialType(item):
    # if ('elev' in item['name'].lower() and 'wall' in item['name'].lower()) or ('elev' in item['name'].lower() and 'pit' in item['name'].lower()):
    if 'elev' in item['name'].lower() and 'pit' in item['name'].lower():
        item['type']="Elevator Pit"
    elif item['name'].lower()[0]=='c' and checkInt(item['name'].lower()[1]):
        item['type']="Columns"
    elif item['name'].lower()[0]=='d' and item['name'].lower()[1]=='p':
        item['type']="Drop Panels"
    elif 'slab step' in item['name'].lower():
        item['type']="Slab Step"
    elif 'slab' in item['name'].lower() or 'sog' in item['name'].lower():
        item['type']="Slab"
    elif 'wall' in item['name'].lower():
        item['type']="Walls"
    elif 'curb' in item['name'].lower():
        item['type']="Curb"
    #Column Cap -> Drop Panel
    elif 'col' in item['name'].lower() and 'cap' in item['name'].lower():
        item['type']="Drop Panels"


def determineProperties(items):
    for item in items:
        words=item['name'].lower().split()
        for i in range(0,len(words)):
            if 'fl' in words[i] or 'fl/' in words[i] or 'floor' in words[i]:
                if 'st' in words[i-1]:
                    n=words[i-1].find('st')
                elif 'nd' in words[i-1]:
                    n=words[i-1].find('nd')
                elif 'rd' in words[i-1]:
                    n=words[i-1].find('rd')
                elif 'th' in words[i-1]:
                    n=words[i-1].find('th')
                item['floor']=int(words[i-1][n-1])

            elif 'found' in words[i] or 'found/' in words[i]:
                item['floor']=1


            if ('part' in words[i] or 'section' in words[i]):
                if i<len(words)-1:
                    if words[i+1].isnumeric():
                        item['section']=int(words[i+1])
                else:
                    x=words[i].split('part')
                    item['section']=int(x[1])

def inferProperties(items, property):
    currentFloor=1
    currentStart=0
    for item in items:
        # print(item['index'])
        if item[property]!=None:
            if item[property]!=currentFloor:
                # print("END "+str(currentFloor)+": "+str(item['index']-1))
                writeGroupFloors(currentFloor, currentStart, item['index']-1, items, property)
                currentStart=item['index']
                currentFloor=item[property]
    writeGroupFloors(currentFloor, currentStart, len(items), items, property)

def writeGroupFloors(floor, start, end, items, property):
    for i in range(start,end):
        items[i][property]=floor

determineProperties(items)
inferProperties(items, 'floor')
inferProperties(items, 'section')

for item in items:
    getMaterialType(item)
    if item['section']!=None and item['floor']!=None and item['type']!=None:
        item['matched']=True




sections={}
for item in items:
    # if item['floor']==1:
    if item['section'] in sections:
        item_list=sections[item['section']]
        item_list.append(item)
        sections[item['section']]=item_list
    else:
        item_list=[item]
        sections.update({item['section']:item_list})

for section in sections:
    floors={}
    print("---------Section "+str(section)+" ----------")
    for item in sections[section]:
        if item['floor'] in floors:
            item_list=floors[item['floor']]
            item_list.append(item)
            floors[item['floor']]=item_list
        else:
            item_list=[item]
            floors.update({item['floor']:item_list})
    
    for floor in floors:
        materialTypes={}
        print("FLOOR: "+str(floor))
        for item in floors[floor]:
            if item['type'] in materialTypes:
                item_list=materialTypes[item['type']]
                item_list.append(item)
                materialTypes[item['type']]=item_list
            else:
                item_list=[item]
                materialTypes.update({item['type']:item_list})

        for materialType in materialTypes:
            print("  "+str(materialType.upper()))
            for item in materialTypes[materialType]:
                print("    - "+str(item['index'])+"  "+item['name']+" - "+str(item['floor'])+"/"+str(item['section']))


print("REMAINING:")
count=0
for item in items:
    if item['matched']==False:
        count+=1
        print("  "+str(item['index'])+"  "+str(item['name'])+"    "+str(item['desc']))
print(count)