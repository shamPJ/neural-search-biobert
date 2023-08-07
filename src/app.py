import dash
import dash_bootstrap_components as dbc
from dash import Dash, dash_table, dcc, html
from ret_sorted_articles import sort_by_similarity

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def article_html(article):
        PMID_similatity = 'PMID: ' + str(article['PMID']) + ' Similarity: ' + str(round(article['Similarity']*100, 2))
        return  html.Div(children=[
                    html.Div(children=[
                        html.Div(children=[ html.H6(article['Title']) ], style = {'textAlign': 'center', 'padding': 10}),
                        html.Div(children=[ html.Label(article['Abstract']) ], style = {'font-size':"12px"}),
                        html.Br(),
                        html.Div(children=[ html.Label(PMID_similatity) ], style = {'font-size':"14px"})
                    ], style = {'border-radius': '5px', 'backgroundColor': '#FFFFFF', 'padding': 15}),
                    html.Br()
                ])

def render(sorted_articles): 
    return [dcc.Checklist(id='checklist-search', options=[ {"label": article_html(article), "value": article['PMID']} for article in sorted_articles ])]

app.layout = html.Div(id='view-body', className='app-body', children=[
        # Head
        html.Div(children=[ html.Label('Neural Search Dashboard')],
                        style={ 'backgroundColor': '#FFFFFF', 'color': '#263238', 
                                'font-family': 'Arial', 'textAlign': 'center', 'padding': 30, 'font-size':"30px"}),
        # Body
        html.Div(children=[
            # Left side (Search and Filters)
            html.Div(children=[
                        # Search
                        html.Div(children=[dcc.Input(id='input-box', type='text', placeholder="Search", style={'width': '70%'}), 
                                        html.Button('Submit', id='button',  n_clicks=0, style={'font-size':"12px"}),
                                        ], style={'textAlign': 'center', 'padding': 10}),
                        # Article type dropdown
                        html.Div(children=[ html.Label('Article type'),
                                        dcc.Dropdown(['Original', 'Review', 'Clinical trials'], 'Original')
                                        ], style={'padding': 20}),
                        # Subject of article dropdown
                        html.Div(children=[ html.Label('Species'),
                                        dcc.Dropdown(['Human', 'Primate', 'Other'], 'Human')],
                                        style={'padding': 20}),
                        html.Div(children=[ html.Label('Entity labels'),
                                        dcc.Checklist(
                                            ['Subject', 'Disease', 'Chemical'], inputStyle={"margin-right": "10px"}, style={'width':'50%'}),
                                        ], style={'padding': 20}),
                        html.Div(children=[ html.Button('Generate summary', id='button-summary', n_clicks=0, style={'font-size':"18px", 'border-radius': '8px', 'backgroundColor': '#ECEFF1'}),
                                        ],style={'textAlign': 'left', 'padding': 10}),

            ], style={'backgroundColor': '#FFFFFF', 'width': '25%', 'margin-top': 40, 'margin-left': 20, 'margin-bottom': 40, 'display': 'inline-block', "verticalAlign": "top"}),

            # Right side (Checklist)
            html.Div(id='output-search', 
            style={"maxHeight": "500px", "overflow": "auto", 'backgroundColor': '#ECEFF1', 'width': '60%', 'margin-top': 40, 'margin-left': 100, 'display': 'inline-block'})
        ])
    ], style = {'font-family': 'Arial', 'color': '#263238', 'backgroundColor': '#ECEFF1'})

@app.callback(
    [dash.dependencies.Output('output-search', 'children')],
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('input-box', 'value')])
def update_output(n_clicks, value):
    print("n_clicks", n_clicks, value)
    if (n_clicks != 0) & (value != None):
        sorted_articles =  sort_by_similarity(value)
        return render(sorted_articles)
    else:
        return dash.no_update

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)