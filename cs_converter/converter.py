import xlrd
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
    item = {'name': name, 'desc': desc, 'qty2': qty2,
            'units2': units2, 'qty1': qty1, 'units1': units1, 'index':row, 'matched':False}
    items.append(item)


def checkInt(x):
    try:
        int(x)
        return True
    except ValueError:
        return False

def checkConsecutive(items_list):
    start=items_list[0]['index']
    end=items_list[0]['index']
    for i in range(1,len(items_list)):
        if items_list[i]['index']-1!=items_list[i-1]['index']:
            end=items_list[i-1]['index']
            print(str(start+1)+"  "+str(end+1))
            start=items_list[i]['index']

elevatorPit=[]
columns=[]
walls=[]
slabSteps=[]
slabs=[]
dropPanels=[]
curbs=[]
colCaps=[]
for i in range(0, len(items)):
    if ('elev' in items[i]['name'].lower() and 'wall' in items[i]['name'].lower()) or ('elev' in items[i]['name'].lower() and 'pit' in items[i]['name'].lower()):
    # if 'elev' in items[i]['name'].lower() and 'pit' in items[i]['name'].lower():
        elevatorPit.append(items[i])
        items[i]['matched']=True
    elif items[i]['name'].lower()[0]=='c' and checkInt(items[i]['name'].lower()[1]):
        columns.append(items[i])
        items[i]['matched']=True
    elif items[i]['name'].lower()[0]=='d' and items[i]['name'].lower()[1]=='p':
        dropPanels.append(items[i])
        items[i]['matched']=True
    elif 'slab step' in items[i]['name'].lower():
        slabSteps.append(items[i])
        items[i]['matched']=True
    elif 'slab' in items[i]['name'].lower() or 'sog' in items[i]['name'].lower():
        slabs.append(items[i])
        items[i]['matched']=True
    elif 'wall' in items[i]['name'].lower():
        walls.append(items[i])
        items[i]['matched']=True
    elif 'curb' in items[i]['name'].lower():
        curbs.append(items[i])
        items[i]['matched']=True
    elif 'col' in items[i]['name'].lower() and 'cap' in items[i]['name'].lower():
        colCaps.append(items[i])
        items[i]['matched']=True

print("ELEVATOR PIT")
for item in elevatorPit:
    print("  "+str(item['name'])+"    "+str(item['desc']))

# print("COLUMNS")
# for item in columns:
#     print("  "+str(item['name'])+"    "+str(item['index']))

checkConsecutive(elevatorPit)
# print("SLAB STEPS")
# for item in slabSteps:
#     print("  "+str(item['name'])+"    "+str(item['desc']))

# print("SLABS")
# for item in slabs:
#     print("  "+str(item['name'])+"    "+str(item['desc']))

# print("DROP PANELS")
# for item in dropPanels:
#     print("  "+str(item['name'])+"    "+str(item['desc']))

# print("WALLS")
# for item in walls:
#     print("  "+str(item['name'])+"    "+str(item['desc']))

# print("CURBS")
# for item in curbs:
#     print("  "+str(item['name'])+"    "+str(item['desc']))

# print("COL CAPS")
# for item in colCaps:
#     print("  "+str(item['name'])+"    "+str(item['desc']))

print("REMAINING:")
count=0
for item in items:
    if item['matched']==False:
        count+=1
        # print("  "+str(item['name'])+"    "+str(item['desc']))
print(count)