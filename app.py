import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

main_df_18 = pd.read_excel('https://github.com/rugpundit/PakistanElectionResults/blob/main/GE%202018%20-%20NA%20(corrected%20results).xlsx?raw=true')
main_df_13 = pd.read_csv('https://raw.githubusercontent.com/AmmarMalik93/Pakistan-Districtwise-Data/main/Elections_2013.csv')

app = Dash(__name__)
server = app.server

app.layout = html.Div(
    children = [
                #html.H2('Number of Votes vs. Percentage of Votes\n'),
                #html.Div(children = "Select the graph:\n", style={"font-weight": "bold"}),
                html.H1(children='Election Data Analysis', style={'text-align':'center', 'font-family':'Roboto, sans-serif',
                  }),
                html.Div(
                  [                
                  dcc.Markdown('Created by [Ammar Malik](https://twitter.com/ammar_malik93)'),
                  dcc.Markdown('Data taken from [rugpundit](https://github.com/rugpundit/PakistanElectionResults) by [Yasir Hussain Sheikh](https://twitter.com/rugpundit)'),
		  dcc.Markdown('[Source Code] (https://github.com/AmmarMalik93/Pakistan-Election-Analysis/blob/main/app.py)'),
                ], 
                style={'font-size':'10px', 'width':'20%', 'borderRadius': 5, 'background-color': '#AEB6BF',
                'border':'thin lightgrey solid', 'font-family':'Roboto, sans-serif'},
                ),
                html.Div(
                    [html.Label(children = "Select the graph:", style={"font-weight": "bold", 'font-family':'Roboto, sans-serif'}),
                     dcc.Dropdown(['Votes vs Percentage', 'Votes vs Rank', 'Candidate Performance', 'Pie Chart'], 'Pie Chart', id='types'),
                     html.Div(id="dd-output-container-1")],
                     style = {"width":"30%", "margin-top":"10px", 'font-family':'Roboto, sans-serif'}, 
                    ),
                
                #html.Div(children = "\nSelect a district:\n", style={"font-weight": "bold"}),
                html.Div(
                    [
                     html.Label(children='Select a district:', style={'font-weight':'bold', 'font-family':'Roboto, sans-serif'}),
                     dcc.Dropdown(np.sort(main_df_18[main_df_18.Province=='Punjab'].District.unique()), 'Lahore', id='district'),
                     html.Div(id="dd-output-container-2")],
                     style = {"width":"30%", "margin-top":"10px", 'font-family':'Roboto, sans-serif'}, 
                    ),
                html.Div(children = "\nSelect political parties:", style={"font-weight":"bold", "margin-top":"10px", 'font-family':'Roboto, sans-serif'}),
                html.Div(
                    [
                     dcc.Checklist(['PML-N', 'PTI', 'PPP'], ['PML-N', 'PTI'], id='parties'),
                    ],
                ),
                html.Div(
                    [html.Label(children='Select the year:', style={'font-weight':'bold', 'font-family':'Roboto, sans-serif'}), 
                     dcc.RadioItems(options=[{'label':'2013', 'value':'2013'}, {'label':'2018', 'value':'2018'}], value='2018', id='year'),
                    ], style = {"width":"30%", "margin-top":"10px"}, 
                ),
                html.Div(
                  [dcc.Graph(id="graph"),
                  ],),
                
                ],
                className='container'
               )

@app.callback(
    Output("graph", "figure"), 
    Input("types", "value"),
    Input("district", "value"),
    Input("year", "value"),    
    Input("parties", "value"))

def update_graph(types, district, year, parties):
  if year== '2018':
    df = main_df_18[main_df_18.District==district]
  else:
    df = main_df_13[main_df_13.District==district]

  df = df.loc[:, ['Constituency', 'Rank', 'Candidate', 'Party', 'Votes']] 
  df['Percent_Votes'] = df.Votes*100/df.groupby('Constituency').Votes.transform('sum')
  if types == 'Pie Chart':
    ds = pd.DataFrame(df[df.Rank==1].groupby('Party')['Party'].count())
    ds.columns = ['Count']
    ds = ds.reset_index(level=0)
    fig = px.pie(ds, values='Count', names='Party', hole=.5, color_discrete_map={"PML-N":"green", "PTI":"red", "PPP":"black"}, color='Party',
             labels={'Count':'Seats Won'})
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(uniformtext_minsize=16, uniformtext_mode='hide',
    annotations=[dict(text='Seats Won', x=0.5, y=0.5, font_size=22, showarrow=False)],
    title = '<b>%s-District-%s</b>'%(district,year), title_x=0.5, font=dict(size=20),  
    hoverlabel=dict(font_size=15),
    legend=dict(x=0,y=1, bgcolor="LightSteelBlue",bordercolor="Black", borderwidth=2,
            font=dict(size=15, color="black")))

  elif types == 'Votes vs Percentage':
    if len(parties)>2:
      fig = px.scatter(df[(df.Party==parties[0])|(df.Party==parties[1])|(df.Party==parties[2])], x="Votes", y="Percent_Votes", color="Party", 
                    hover_data=['Candidate'], color_discrete_map={"PML-N":"green", "PTI":"red", "PPP":"black"})
    else:
      fig = px.scatter(df[(df.Party==parties[0])|(df.Party==parties[1])], x="Votes", y="Percent_Votes", color="Party", 
                    hover_data=['Candidate'], color_discrete_map={"PML-N":"green", "PTI":"red", "PPP":"black"})

    fig.update_traces(marker=dict(size=12, line=dict(width=2)), selector=dict(mode='markers'))

    fig.update_xaxes(title_text = "<b>Votes</b>", title_font = {"size": 15}, title_standoff = 10)

    fig.update_yaxes(title_text = "<b>Percentage Votes</b>", title_font = {"size": 15}, title_standoff = 10)

    fig.update_layout(legend=dict(x=0,y=1, bgcolor="LightSteelBlue",bordercolor="Black", borderwidth=2,
            font=dict(size=15, color="black")), width=800, height=400, title = '<b>%s-District-%s</b>'%(district,year), title_x=0.5, font=dict(size=20),
            hoverlabel=dict(font_size=15))

    fig.add_hline(y=df[df.Rank==1].Percent_Votes.mean(), line_width=1, line_dash="dash", line_color="black",
                annotation_text='<b>Average<br> Win Pct.<br> : %.1f</b>'%df[df.Rank==1].Percent_Votes.mean(), annotation_font_size=16, annotation_position="right", annotation_font_color="black")

  elif types == 'Votes vs Rank':
    fig = px.scatter(df[(df.Party==parties[0])], x="Rank", y="Percent_Votes", color="Party", 
                    hover_data=['Candidate'], color_discrete_map={"PML-N":"green", "PTI":"red", "PPP":"black"})

    fig.update_traces(marker=dict(size=12, line=dict(width=2)), selector=dict(mode='markers'))

    fig.update_xaxes(title_text = "<b>Final Position</b>", title_font = {"size": 15}, title_standoff = 10)

    fig.update_yaxes(title_text = "<b>Percentage Votes</b>", title_font = {"size": 15}, title_standoff = 10)

    fig.update_layout(width=800, height=400, title = '<b>%s-District-%s-%s</b>'%(district,year,parties[0]), title_x=0.5, font=dict(size=20),
            hoverlabel=dict(font_size=15), xaxis = dict(tickmode = 'array',tickvals = [1, 2, 3], ticktext = ['<b>First</b>', '<b>Second</b>', '<b>Third</b>']),
            )
  
  else: #if types == 'Candidate Performance':#else:
    if len(parties)>2:
      fig = px.bar(df[(df.Party==parties[0])|(df.Party==parties[1])|(df.Party==parties[2])], x="Percent_Votes", y="Constituency", color="Party", text='Candidate', 
                hover_data=['Candidate'], color_discrete_map={"PML-N":"green", "PTI":"red", "PPP":"black"}, barmode='group')
    else:
      fig = px.bar(df[(df.Party==parties[0])|(df.Party==parties[1])], x="Percent_Votes", y="Constituency", color="Party", text='Candidate', 
                hover_data=['Candidate'], color_discrete_map={"PML-N":"green", "PTI":"red", "PPP":"black"}, barmode='group')


    fig.update_traces(textposition='inside', textfont_size=16)

    fig.update_xaxes(title_text = "<b>Percentage Votes (%) </b>",title_font = {"size": 15},title_standoff = 10)

    fig.update_yaxes(title_text = "<b>Constituency</b>",title_font = {"size": 15},title_standoff = 10)

    fig.update_layout(legend=dict(font=dict(size=20,color="black"),
        bgcolor="LightSteelBlue", bordercolor="Black", borderwidth=2),
    width=1200, height=800, title = '<b>%s-District-%s</b>'%(district,year), title_x=0.5, font=dict(size=20),
          hoverlabel=dict(font_size=15))

    fig.add_vline(x=df[df.Rank==1].Percent_Votes.mean(), line_width=2, line_dash="dash", line_color="black",
                annotation_text='<b>Average Win Pct: %.1f</b>'%df[df.Rank==1].Percent_Votes.mean(), annotation_font_size=16, annotation_position="top", annotation_font_color="black")


  return fig


if __name__ == '__main__':
	app.run_server(debug=True)
