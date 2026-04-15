import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Carga tu dataset
df = pd.read_csv('spacex_launch_dash.csv')

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=9600,
        step=100,
        marks={0: '0', 2400: '2400', 4800: '4800', 7200: '7200', 9600: '9600'},
        value=[0, 9600]
    ),
    dcc.Graph(id='success-pie-chart'),
    dcc.Graph(id='success-payload-scatter-chart'),
])
# Callback para el pie chart

@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_pie_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = df[(df['Payload Mass (kg)'] >= low) & (df['Payload Mass (kg)'] <= high)]
    
    if selected_site == 'ALL':
        success_counts = filtered_df[filtered_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Successes']
        fig = px.pie(success_counts, values='Successes', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        df_plot = filtered_df[
            (filtered_df['Launch Site'] == selected_site) & 
            (filtered_df['class'] == 1)
        ]
        fig = px.pie(df_plot, names='class', title=f'Success Launches for site {selected_site}')
    return fig
#Callback para el scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = df[(df['Payload Mass (kg)'] >= low) & (df['Payload Mass (kg)'] <= high)]
    
    if selected_site == 'ALL':
        df_plot = filtered_df
        title = 'Payload vs. Launch Outcome for All Sites'
    else:
        df_plot = filtered_df[filtered_df['Launch Site'] == selected_site]
        title = f'Payload vs. Launch Outcome for site {selected_site}'
    
    if df_plot.empty:
        fig = px.scatter(title='No data available for selected filters')
    else:
        fig = px.scatter(
            df_plot, x='Payload Mass (kg)', y='class',
            color='Booster Version',
            title=title,
            labels={'class': 'Launch Outcome (0=Failure, 1=Success)', 'Payload Mass (kg)': 'Payload Mass (kg)'}
        )
    return fig

if __name__ == '__main__':
    app.run(debug=True)
