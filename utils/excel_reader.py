# utils/excel_reader.py
import pandas as pd
import os

def read_excel_names(file_path='Names.xlsx', sheet_name='sheet'):
    """
    Read names from Excel file and return the first name
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        names_list = df['Name'].dropna().tolist()
        
        if not names_list:
            print("❌ The name list is empty. Please check the Excel file.")
            return None
        
        first_name = names_list[0]
        print(f"✅ First name extracted: {first_name}")
        return first_name
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return None
