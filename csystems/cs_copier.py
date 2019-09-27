# Reading an excel file using Python
import xlrd
import xlsxwriter
from openpyxl import load_workbook
# from openpyxl import Workbook

# Give the location of the file
takeoff_doc = '/Users/rwilk193/OtherProjects/Misc/csystems/Document #2 (After).xlsx'
estimate_doc = '/Users/rwilk193/OtherProjects/Misc/csystems/COST SPREADSHEET.xlsx'
result_doc='/Users/rwilk193/OtherProjects/Misc/csystems/COST SPREADSHEET - Modified.xlsx'
wb=load_workbook(estimate_doc)

# To open Workbook
takeoff = xlrd.open_workbook(takeoff_doc)
estimate = xlrd.open_workbook(estimate_doc)

floors = []
reinforcing = []
categories = []
source_sheet = takeoff.sheet_by_index(0)
target_sheet = estimate.sheet_by_name('ESTIMATE')


class DataBlock:
    def __init__(self, name, start):
        self.name = name
        self.start = start
        self.end = -1
        self.target = -1

    def __str__(self):
        return self.name+": "+str(self.start)+" -> "+str(self.end)+"  ("+str(self.target)+")"


# SEARCH FOR EACH FLOOR
for row in range(source_sheet.nrows):
    col = 0
    # print(source_sheet.cell(row,col).value)
    if source_sheet.cell(row, col).value.lower() == 'foundation':
        floors.append(row)
    elif 'floor' in str(source_sheet.cell(row, col).value).lower() and str(source_sheet.cell(row-1, col).value) == "":
        floors.append(row)

print(floors)

# ITERATE THROUGH FLOORS/SECTIONS
floor=0

# SEARCH FOR EACH CATEGORY
for row in range(floors[floor]+1, floors[floor+1]):
    val = str(source_sheet.cell(row, col).value)
    if (val.isupper() and not any(char.isdigit() for char in val)):
        if val.lower().strip() == 'reinforcing':
            reinforcing.append(row)
        else:
            categories.append(DataBlock(val.lower(), row))
        # print(source_sheet.cell(row,col).value)


#BREAK ESTIMATE UP INTO FLOORS FIRST, THEN SEARCH ONLY WITHIN THE FLOOR

target_locations={}
# GET TARGET SHEET FLOORS
for row in range(target_sheet.nrows):
    col = 0
    val = str(target_sheet.cell(row, col).value).lower().strip()
    if (len(val)<10 and val[-5:]=="level") or val=="foundation" or val=="main roof":
        target_locations.update({len(target_locations): row})

print(target_locations)


# SEARCH FOR EACH ITEMS
for index in range(len(categories)):

    # SET SIZE OF LOOP
    if len(categories) < index:
        rangeVals = range(categories[index].start+2,
                          categories[index+1].start-1)
    else:
        rangeVals = range(categories[index].start+2, floors[floor+1])

    for row in rangeVals:
        val = str(source_sheet.cell(row, col).value)
        if len(val) == 0:
            categories[index].end = row+1
            # print("END: "+str(row+1))
            break 
        # else:
        #     print(val)

    # FIND START POINT ON ESTIMATE
    for row in range(target_locations[floor], target_locations[floor+1]):
        val = str(target_sheet.cell(row, col).value).lower().strip()
        # print(str(row)+") "+val+"-"+categories[index].name+"  "+str(val == categories[index].name))
        if val == categories[index].name:
            categories[index].target=row+2
            break

# GET ESTIMATE FILE WITH OPENPYXL
estimate_sheets=wb.sheetnames
if "ESTIMATE" not in estimate_sheets:
    print ("Sheet with name 'ESTIMATE' is missing from Estimate workbook")
    exit(1)

worksheet=wb['ESTIMATE']
inserts=0
for cat in categories:
    for source_row in range(cat.start+2, cat.end-1):
        # print("INSERT "+cat.name+" AT "+str(cat.target+inserts))
        if source_row>cat.start+2:
            worksheet.insert_rows(cat.target+inserts) 
        
        for col in range(0,5):
            val=source_sheet.cell(source_row,col).value
            # print(val)
            if cat.target > 0:
                print(str(val)+" - ("+str(col+1)+","+str(cat.target+inserts)+")")
                worksheet.cell(column=col+1, row=cat.target+inserts, value=val)
        inserts+=1
    inserts-=1
wb.save(result_doc)