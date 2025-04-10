from flask import Flask, render_template, request
import pandas as pd
import re

app = Flask(__name__)

# Load the Excel file with two sheets:
# - Sheet 1: Contains "Family index", "Similar 1", "Similar 2", and "Similar 3"
# - Sheet 2: Contains "Family index" and "Description"
excel_file = pd.ExcelFile('family_similarity_results.xlsx')
df_sheet1 = pd.read_excel(excel_file, sheet_name=0)
df_sheet2 = pd.read_excel(excel_file, sheet_name=1)

# Define a simple function to extract the number from the "Familly XXX" string
def extract_number(family_str):
    match = re.search(r'\d+', str(family_str))
    if match:
        return int(match.group())
    return None

# Add a column 'family_number' to each dataframe for easier lookups
df_sheet1['family_number'] = df_sheet1['Family Index'].apply(extract_number)
df_sheet2['family_number'] = df_sheet2['Family Index'].apply(extract_number)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        number_input = request.form.get('number')
        try:
            # Convert input to an integer (or float if needed)
            number = int(number_input)
        except ValueError:
            error = "Please enter a valid number."
            return render_template('index.html', error=error)

        # Lookup the family number in the first sheet
        match1 = df_sheet1[df_sheet1['family_number'] == number]
        if not match1.empty:
            similar1 = match1.iloc[0].get('Similar 1', 'N/A')
            similar2 = match1.iloc[0].get('Similar 2', 'N/A')
            similar3 = match1.iloc[0].get('Similar 3', 'N/A')
        else:
            similar1, similar2, similar3 = "No match", "No match", "No match"

        # Lookup the family number in the second sheet for the description
        match2 = df_sheet2[df_sheet2['family_number'] == number]
        if not match2.empty:
            description = match2.iloc[0].get('description', 'No description available.')
        else:
            description = "No description available."

        return render_template(
            'result.html',
            number=number,
            similar1=similar1,
            similar2=similar2,
            similar3=similar3,
            description=description
        )
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
