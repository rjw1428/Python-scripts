# Reading an excel file using Python
import xlrd

# Give the location of the file
takeoff_doc = './cs_converter/Document #2 (After).xlsx'
estimate_doc = './cs_converter/COST SPREADSHEET.xlsx'

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

# SEARCH FOR EACH CATEGORY
for row in range(floors[0]+1, floors[1]):
    val = str(source_sheet.cell(row, col).value)
    if (val.isupper() and not any(char.isdigit() for char in val)):
        if val.lower().strip() == 'reinforcing':
            reinforcing.append(row)
        else:
            categories.append(DataBlock(val.lower(), row))
        # print(source_sheet.cell(row,col).value)



# SEARCH FOR EACH ITES
for index in range(len(categories)):

    # SET SIZE OF LOOP
    if len(categories) < index:
        rangeVals = range(categories[index].start+2,
                          categories[index+1].start-1)
    else:
        rangeVals = range(categories[index].start+2, floors[1])

    for row in rangeVals:
        val = str(source_sheet.cell(row, col).value)
        if len(val) == 0:
            categories[index].end = row+1
            # print("END: "+str(row+1))
            break 
        # else:
        #     print(val)

#BREAK ESTIMATE UP INTO FLOORS FIRST, THEN SEARCH ONLY WITHIN THE FLOOR

    # FIND START POINT ON ESTIMATE
    col=0
    for row in range(target_sheet.nrows):
        val = str(target_sheet.cell(row, col).value).lower().strip()
        # print(str(row)+") "+val+"-"+categories[0].name+"-")
        if val == categories[index].name:
            categories[index].target=row
            # print(row)
            break


for cat in categories:
    print(cat)