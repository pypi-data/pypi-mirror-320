import os
import webbrowser
import pandas as pd
from dash import Dash, Input, Output, dash_table, dcc, html

from modules.fimport import path_output

# load log file
def parse_log_file(file_path):
    try:
        with open(file_path, 'r', encoding='latin1') as file:
            lines = file.readlines()
        data = []
        for line in lines:
            parts = line.split('\t')
            if len(parts) >= 6:
                timestamp, level, source, id_info, code, message = parts[:6]
                date, time = timestamp.split('T') if 'T' in timestamp else (timestamp, '')
                data.append({
                    'Date': date,
                    'Time': time,
                    'Level': level,
                    'Source': source,
                    'ID Info': id_info,
                    'Code': code.strip(),
                    'Message': message.strip()
                })
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return pd.DataFrame()

# Initialize app
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Elite Log Viewer"

# List of log files to choose from
log_files = [
    'Surgery-Default.log',
    'Surgery-Debug.log',
    'Surgery-Software-Reserved.log',
    'Surgery-Installer.log',
    'startupApp.log'
]
log_files_options = [{'label': file, 'value': file} for file in log_files]

# Default data
selected_file = os.path.join(path_output, log_files[0])
df = parse_log_file(selected_file)

"""
df = pd.DataFrame(data)
levels = [{'label': lvl, 'value': lvl} for lvl in sorted(df['Level'].dropna().unique())]
sources = [{'label': src, 'value': src} for src in sorted(df['Source'].dropna().unique())]
codes = [{'label': code, 'value': code} for code in sorted(df['Code'].dropna().unique())]
print("DataFrame columns:", df.columns)
"""
    
if not df.empty:
    url = "http://127.0.0.1:8050"
    webbrowser.open_new(url)
    
"""    
except Exception as e:
    print(f"Unable to read file: {e}")
    df = pd.DataFrame()
    levels = sources = codes = []
  

# Create app Dash
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Elite Log Viewer"

# Level available (update with real value)
levels = []
for lvl in sorted(df['Level'].dropna().unique()):
    levels.append({'label': lvl, 'value': lvl})
"""
# Layout
app.layout = html.Div([
    html.H1("Elite Log Viewer"),
    html.Div([
        html.Label("Select Log File"),
        dcc.Dropdown(
            id='log-file-selector',
            options=log_files_options,
            value=log_files[0],
            style={'width': '300px'}
        ),
    ], style={'margin-bottom': '20px'}),

    html.Div([
        dcc.DatePickerSingle(
            id='filter-date',
            placeholder='Date',
            display_format='YYYY-MM-DD',
            style={'width': 200, 'height': 30, 'border-color': '#DFE6E9', 'textAlign': 'left', 'font-size': '10px'}
        ),
        html.Div([
            html.Label("Level Filter"),
            dcc.Checklist(
                id='filter-level',
                options=[],
                value=[],
            ),
        ]),
        dcc.Dropdown(
            id='filter-source',
            options=[],
            placeholder='Source Filter',
            style={'width': 200, 'height': 40, 'border-color': '#DFE6E9', 'textAlign': 'left', 'font-size': '12px'}
        ),
        dcc.Dropdown(
            id='filter-code',
            options=[],
            placeholder='Code Filter',
            style={'width': 200, 'height': 40, 'border-color': '#DFE6E9', 'textAlign': 'left', 'font-size': '12px'}
        ),
        dcc.Input(
            id='search-message',
            type='text',
            placeholder='Message Filter',
            style={'width': 200, 'height': 40, 'border-color': '#DFE6E9', 'textAlign': 'left', 'font-size': '14px'}
        ),
    ], style={'margin-bottom': '20px'}),

    dash_table.DataTable(
        id='log-table',
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=df.to_dict('records'),
        page_size=50,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px', 'whiteSpace': 'normal', 'height': 'auto'},
    )
])

# Callbacks
@app.callback(
    [Output('log-table', 'data'),
     Output('log-table', 'columns'),
     Output('filter-level', 'options'),
     Output('filter-source', 'options'),
     Output('filter-code', 'options')],
    [Input('log-file-selector', 'value'),
     Input('filter-date', 'date'),
     Input('filter-level', 'value'),
     Input('filter-source', 'value'),
     Input('filter-code', 'value'),
     Input('search-message', 'value')]
)
def update_table(log_file, filter_date, filter_levels, filter_source, filter_code, search_message):
    file_path = os.path.join(path_output, log_file)
    filtered_df = parse_log_file(file_path)

    if filter_date:
        filtered_df = filtered_df[filtered_df['Date'] == filter_date]
    if filter_levels:
        filtered_df = filtered_df[filtered_df['Level'].isin(filter_levels)]
    if filter_source:
        filtered_df = filtered_df[filtered_df['Source'] == filter_source]
    if filter_code:
        filtered_df = filtered_df[filtered_df['Code'] == filter_code]
    if search_message:
        filtered_df = filtered_df[filtered_df['Message'].str.contains(search_message, case=False, na=False)]

    level_options = [{'label': lvl, 'value': lvl} for lvl in sorted(filtered_df['Level'].dropna().unique())]
    source_options = [{'label': src, 'value': src} for src in sorted(filtered_df['Source'].dropna().unique())]
    code_options = [{'label': code, 'value': code} for code in sorted(filtered_df['Code'].dropna().unique())]

    return filtered_df.to_dict('records'), [{'name': col, 'id': col} for col in filtered_df.columns], level_options, source_options, code_options

if __name__ == "__main__":
    app.run_server(debug=False)

