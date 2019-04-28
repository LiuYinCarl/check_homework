from openpyxl import Workbook


def export_excel(data, email):
    wb = Workbook()
    ws = wb.active
    print(data)
    for i in range(len(data)):
        for j in range(len(data[0])):
            c = ws.cell(row=i + 1, column=j + 1)
            c.value = data[i][j]
    name = email + '.xlsx'
    wb.save(name)


data = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],

]
email = 'ddf@qq.com'

export_excel(data, email)
