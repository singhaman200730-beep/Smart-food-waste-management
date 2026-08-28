import pandas as pd

file = "food_waste.xlsx"

print("Reading Excel file...")

excel_data = pd.ExcelFile(file)

print("Sheets available:")
print(excel_data.sheet_names)

for sheet in excel_data.sheet_names:
    print("\n==============================")
    print("SHEET:", sheet)
    print("==============================")

    df = pd.read_excel(file, sheet_name=sheet)

    print("Columns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())