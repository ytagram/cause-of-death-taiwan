import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import json
# import plotly.graph_objects as go
# import geopandas
# import numpy as np
# import dash_bootstrap_components as dbc

app = Dash(__name__)
server = app.server

# -- Import and clean data (importing csv into pandas)
df = pd.read_csv("cause_of_death.csv")
df['state'] = df['country'].str[:3]


# shp_file = geopandas.read_file('COUNTY_MOI_1090820.shp', encoding='utf8')
# shp_file.to_file('COUNTY_MOI_1090820.geojson', driver='GeoJSON', epsg=4326)  # 經緯度由epsg3826(TWD97)轉換為epsg4326(WGS84)

with open('COUNTY_MOI_1090820.geojson', encoding='utf8') as response:
    mapGeo = json.load(response)

df2 = pd.DataFrame.from_dict([i['properties'] for i in mapGeo['features']])

df = df.merge(df2, how='left', left_on='state', right_on='COUNTYNAME')

df3 = df.groupby(['category'])[['N']].sum()

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.Div([
        html.Div([
            html.H1("台灣各年度死因調查", style={'text-align': 'center'}),
            html.Span("年度", style={'text-align': 'left'}),
            dcc.Dropdown(id="slct_year",
                    options=[
                        {"label": "110", "value": 110},
                        {"label": "109", "value": 109},
                        {"label": "108", "value": 108},
                        {"label": "107", "value": 107},
                        {"label": "106", "value": 106},
                        {"label": "105", "value": 105},
                        {"label": "104", "value": 104},
                        {"label": "103", "value": 103},
                        {"label": "102", "value": 102},
                        {"label": "101", "value": 101}],
                    multi=False,
                    value=110,
                    style={'width': '50%'}
                ),
            html.Br(),

            html.Div([
            html.Div(dcc.Graph(id='bar', figure={})),
            html.Div(dcc.Graph(id='scatter', figure={}))
            ],style = {'display': 'flex'}),
            html.Br(),

            html.Span("死因種類", style={'text-align': 'left'}),
            dcc.Dropdown(
                    id="slct_cate",
                    options=[
                        {"label": "內分泌、營養及新陳代謝疾病", "value": "內分泌、營養及新陳代謝疾病"},
                        {"label": "呼吸系統疾病", "value": "呼吸系統疾病"},
                        {"label": "導致罹病或致死之外因", "value": "導致罹病或致死之外因"},
                        {"label": "血液和造血器官及涉及免疫機轉的特定疾患", "value": "血液和造血器官及涉及免疫機轉的特定疾患"},
                        {"label": "泌尿生殖系統疾病", "value": "泌尿生殖系統疾病"},
                        {"label": "消化系統疾病", "value": "消化系統疾病"},
                        {"label": "特定感染症及寄生蟲疾病", "value": "特定感染症及寄生蟲疾病"},
                        {"label": "神經系統疾病", "value": "神經系統疾病"},
                        {"label": "症狀、徵候與他處未歸類之異常臨床及實驗室發現", "value": "症狀、徵候與他處未歸類之異常臨床及實驗室發現"},
                        {"label": "腫瘤", "value": "腫瘤"},
                        {"label": "精神與行為障礙", "value": "精神與行為障礙"},
                        {"label": "循環系統疾病", "value": "循環系統疾病"},
                        {"label": "源於周產期的特定病況", "value": "源於周產期的特定病況"}],
                    multi=False,
                    value="內分泌、營養及新陳代謝疾病",
                    style={'width': '50%'}
                ),
            html.Br(),
            html.Span("死因", style={'text-align': 'left'}),
            dcc.Dropdown(
                    id="slct_reason",
                    options={},
                    multi=False,
                    value="糖尿病",
                    style={'width': '50%'}
                ),
        ]),
        html.Br(),
        html.Div([
            html.Div(dcc.Graph(id='map', figure={})),
            html.Div(dcc.Graph(id='linechart', figure={}))
        ],style = {'display': 'flex'}),
        html.Div([
            html.Div(dcc.Graph(id='map2', figure={})),
            html.Div(dcc.Graph(id='linechart2', figure={}))
        ],style = {'display': 'flex'}),
    ]),
])

# ------------------------------------------------------------------------------


# Connect the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='slct_reason', component_property='options'),
    [Input(component_id='slct_cate', component_property='value')]
)

def update_dp(option_slctd):

    neww = df[df['category']== option_slctd].groupby(['reason'])[['N']].sum()
    neww.reset_index(inplace=True)
    a = neww['reason'].tolist()

    return [{'label': i, 'value': i} for i in a]

@app.callback(
    [Output(component_id='bar', component_property='figure'),
        Output(component_id='map', component_property='figure'),
        Output(component_id='linechart', component_property='figure'),
        Output(component_id='map2', component_property='figure'),
        Output(component_id='linechart2', component_property='figure'),
        Output(component_id='scatter', component_property='figure')],
    [Input(component_id='slct_year', component_property='value'),
        Input(component_id='slct_reason', component_property='value')]
)
def update_graph(option_slctd,option_slctd_2):
    
    category = df.loc[(df["reason"] == option_slctd_2),'category'].values[0]
    dff = df.copy()
    dff2 = df.copy()
    dff3 = df.copy()
    dff4 = df.copy()
    dff5 = df.copy()
    dff6 = df.copy()
    dff = dff[dff["year"] == option_slctd]
    dff2 = dff2[(dff2["category"] == category) & (dff2["year"] == option_slctd)]
    dff4 = dff4[(dff4["reason"] == option_slctd_2) & (dff4["year"] == option_slctd)]
    dff3 = dff3[dff3["category"] == category]
    dff5 = dff5[dff5["reason"] == option_slctd_2]
    dff6 = dff6[dff6["year"] == option_slctd]
    reason = option_slctd_2
    year = str(option_slctd)

    new = dff.groupby(['year','category'])[['N']].sum()
    new.reset_index(inplace=True)
    new = new.sort_values(by='N', ascending = True)
    new2 = dff2.groupby(['year', 'COUNTYCODE', 'COUNTYNAME','category'])[['N']].sum()
    new2.reset_index(inplace=True)
    new3 = dff3.groupby(['year','category'])[['N']].sum()
    new3.reset_index(inplace=True)
    new4 = dff4.groupby(['year', 'COUNTYCODE', 'COUNTYNAME','reason'])[['N']].sum()
    new4.reset_index(inplace=True)
    new5 = dff5.groupby(['year','reason'])[['N']].sum()
    new5.reset_index(inplace=True)
    new6 = dff6.groupby(['year','category','age'])[['N']].sum()
    new6.reset_index(inplace=True)

    # Plotly Express
    fig =  px.bar(new, x='N', y='category')
    fig.update_layout(title=year + " " + "年度" + "各死亡原因人數分布" ,title_x=0.5)
    fig6 = px.scatter(new6, x="age", y="N",color="category")
    fig6.update_xaxes(categoryorder='array', categoryarray= ['0-9歲', '10-19歲', '20-29歲','30-39歲','40-49歲','50-59歲','60-69歲','70-79歲','80-89歲','90-99歲','100歲以上',])
    fig6.update_layout(title=year + " " + "年度" + "各死亡原因人數年齡分布" ,title_x=0.5)
    fig2 = px.choropleth_mapbox(
                            new2,
                            geojson=mapGeo,
                            locations='COUNTYCODE',
                            featureidkey='properties.COUNTYCODE',
                            color='N',
                            color_continuous_scale='Greys',
                            range_color=(0,new2['N'].max()),
                            mapbox_style='carto-positron',
                            zoom=5.5,
                            center={'lat': 23.5832, 'lon': 120.5825},
                            opacity=0.5,
                            hover_data=['category','COUNTYNAME', 'year', 'N']
                          )
    fig2.update_layout(title=category+ " " + "各縣市死亡人數分布" ,title_x=0.5)

    fig4 = px.choropleth_mapbox(
                            new4,
                            geojson=mapGeo,
                            locations='COUNTYCODE',
                            featureidkey='properties.COUNTYCODE',
                            color='N',
                            color_continuous_scale='Greys',
                            range_color=(0,new4['N'].max()),
                            mapbox_style='carto-positron',
                            zoom=5.5,
                            center={'lat': 23.5832, 'lon': 120.5825},
                            opacity=0.5,
                            hover_data=['reason','COUNTYNAME', 'year', 'N']
                          )
    fig4.update_layout(title=reason + " " + "各縣市死亡人數分布" ,title_x=0.5)

    fig3 =  px.line(new3, x="year", y="N",hover_data=['category', 'year', 'N'])
    fig3.update_layout(title=category+ " " + "歷年死亡人數趨勢" ,title_x=0.5)
    fig5 =  px.line(new5, x="year", y="N",hover_data=['reason', 'year', 'N'])
    fig5.update_layout(title=reason+ " " + "歷年死亡人數趨勢" ,title_x=0.5)

    return fig, fig2, fig3, fig4, fig5, fig6


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server()