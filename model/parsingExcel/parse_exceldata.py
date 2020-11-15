import os
import xlrd
import csv

loc = os.path.join(os.getcwd(), "Justo_10-14-19_to_11-14-20.xlsx")
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

num_rows = sheet.nrows

# array that csv will read from
to_csv = []

for i in range(num_rows):
    row = sheet.row_values(i)
    if row[0][0:2] == '20':  # rows where we have actual data
        # month / day
        date = row[0].split()
        format_date = date[0].split('-')
        date_str = format_date[1] + '/' + format_date[2]

        to_csv.append([date_str, date[1], row[1]])

        print("{}, {}, {}".format(
            date_str, date[1], row[1]))


# add data to csv file
with open('Justo_house.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for element in to_csv:
        writer.writerow(element)
