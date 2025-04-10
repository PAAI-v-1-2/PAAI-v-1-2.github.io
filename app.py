from flask import Flask, render_template, request
import pandas as pd
import re

app = Flask(__name__)


excel_file = pd.ExcelFile('family_similarity_results.xlsx')
df_sheet1 = pd.read_excel(excel_file, sheet_name="Similar Families")
df_sheet2 = pd.read_excel(excel_file, sheet_name="Family Descriptions")

def extract_number(family_str):
    match = re.search(r'\d+', str(family_str))
    if match:
        return int(match.group())
    return None

df_sheet1['family_number'] = df_sheet1['Family Index'].apply(extract_number)
df_sheet2['family_number'] = df_sheet2['Family Index'].apply(extract_number)

def get_similar_data(similar_value):
    if similar_value == "No match":
        return {"id": None, "description": None}
    if similar_value is None:
        return {"id": None, "description": None}
    match_desc = df_sheet2[df_sheet2['family_id'] == similar_value]
    if not match_desc.empty:
        desc = match_desc.iloc[0].get('description', 'No description available.')
    else:
        desc = "No description available."
    return {"id": similar_value, "description": desc}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        number_input = request.form.get('number')
        try:
            number = int(number_input)
        except ValueError:
            error = "Please enter a valid number."
            return render_template('index.html', error=error)

        # Lookup in the first sheet
        match1 = df_sheet1[df_sheet1['family_number'] == number]
        if not match1.empty:
            similar1 = match1.iloc[0].get('Similar 1', 'No match')
            similar2 = match1.iloc[0].get('Similar 2', 'No match')
            similar3 = match1.iloc[0].get('Similar 3', 'No match')
        else:
            similar1, similar2, similar3 = "No match", "No match", "No match"

        # Lookup for the primary family description
        match2 = df_sheet2[df_sheet2['family_number'] == number]
        if not match2.empty:
            description = match2.iloc[0].get('description', 'No description available.')
        else:
            description = "No description available."

        # Build list of dictionaries for the similar families
        similar_data = [
            get_similar_data(similar1),
            get_similar_data(similar2),
            get_similar_data(similar3)
        ]

        return render_template(
            'result.html',
            number=number,
            description=description,
            similar_data=similar_data
        )
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
