# Hands-On Lab: Build an Interactive Dashboard with Plotly Dash
# Student: Luis F. Cisneros
# Last update: 2024/10/27

# Required libraries
import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Create dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Open Dash App
app = Dash(__name__)

# Create Layout for App
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown 
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                {'label': 'All Sites', 'value': 'ALL'},
                                                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                                ],
                                             value='ALL',
                                             placeholder='Select a Launch Site here',
                                             searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart for Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, 
                                    max=10000, 
                                    step=1000,
                                    marks={0: '0', 1000: '1000', 5000: '5000', 10000: '10000'},  # Updated for clearer intervals
                                    value=[min_payload, max_payload]
                                ),
                                # TASK 4: Add a scatter chart to visualize payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function to render success-pie-chart based on selected site dropdown
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    # Define a color map for the sites (optional, for specific colors)
    color_map = {
        'KSC LC-39A': 'blue',
        'CCAFS LC-40': 'red',
        'VAFB SLC-4E': 'green',
        'CCAFS SLC-40': 'purple'
    }
    
    # Check if 'ALL' sites are selected
    if entered_site == 'ALL':
        # Use the entire dataframe to show total success launches for all sites
        # Group by 'Launch Site' and count successful launches (class == 1)
        total_success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        total_success_counts.columns = ['Launch Site', 'Success Count']
        
        # Create the pie chart figure
        fig = px.pie(total_success_counts, values='Success Count', names='Launch Site', 
                     title='Total Success Launches by Site')
        
        # Apply color mapping to each site in the pie chart
        fig.update_traces(marker=dict(colors=[color_map[site] for site in total_success_counts['Launch Site']]))
        
    else:
        # Filter the dataframe for the selected site to show success vs failure counts
        site_data = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_fail_counts = site_data['class'].value_counts().reset_index()
        success_fail_counts.columns = ['class', 'count']
        
        # Create the pie chart for success vs failure for the specific site
        fig = px.pie(success_fail_counts, values='count', names='class', 
                     title=f"Launch Outcomes for {entered_site}")
        
        # Set specific colors for success and failure
        fig.update_traces(marker=dict(colors=['blue', 'red']))  # blue for success, red for failure

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def scatter(entered_site, payload):
    filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload[0], payload[1])]
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category', 
                         title='Success count on Payload mass for all sites')
    else:
        fig = px.scatter(filtered_df[filtered_df['Launch Site'] == entered_site], 
                         x='Payload Mass (kg)', y='class', color='Booster Version Category', 
                         title=f"Success count on Payload mass for site {entered_site}")
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port=8060)