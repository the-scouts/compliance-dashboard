import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

from page_components.navbar import Navbar

# Type hints:
from dash import Dash


body = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("Heading"),
                        html.P(
                            '''
                           Donec id elit non mi porta gravida at eget metus.Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentumnibh, ut fermentum massa justo sit amet risus. Etiam porta semmalesuada magna mollis euismod. Donec sed odio dui. Donec id elit nonmi porta gravida at eget metus. Fusce dapibus, tellus ac cursuscommodo, tortor mauris condimentum nibh, ut fermentum massa justo sitamet risus. Etiam porta sem malesuada magna mollis euismod. Donec sedodio dui.
                            '''
                        ),
                        dbc.Button("View details",color="secondary"),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.H2("This is the world's best graph"),
                        dcc.Graph(
                            figure={"data":[{'x':[1,2,3], 'y':[1,4,9]}]}
                        ),
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("This is my second graph"),
                        dcc.Graph(
                            figure=go.Figure(data=[go.Pie(labels=['Pie Eaten'], values=[1])])
                        )
                    ]
                ),
                dbc.Col(
                    [
                        html.H2('This is a paragraph from a Harry Potter: The Philosopher Stone'),
                        dbc.DropdownMenu(
                            id='my-dropdown',
                            label="Pick a paragraph",
                            children=[
                                dbc.DropdownMenuItem('Paragraph 1'),
                                dbc.DropdownMenuItem(divider=True),
                                dbc.DropdownMenuItem('Paragraph 2'),
                                dbc.DropdownMenuItem(divider=True),
                                dbc.DropdownMenuItem('Paragraph 2'),
                            ]
                        ),
                        html.P(
                            '''
                            Mr. and Mrs. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much. They were the last people you'd expect to be involved in anything strange or mysterious, because they just didn't hold with such nonsense. Mr. Dursley was the director of a firm called Grunnings, which made drills. He was a big, beefy man with hardly any neck, although he did have a very large mustache. Mrs. Dursley was thin and blonde and had nearly twice the usual amount of neck, which came in very useful as she spent so much of her time craning over garden fences, spying on the neighbors. The Dursleys had a small son called Dudley and in their opinion there was no finer boy anywhere.
                            '''
                        ),
                        dbc.Button("Source", color="secondary", href='http://www.hogwartsishere.com/library/book/7107/chapter/1/')
                    ]
                )
            ]
        )
    ],
    className="mt-4",
)


def Homepage(app: Dash):
    return html.Div([
        Navbar(app),
        body
    ])


# app.layout = Homepage()
'''
@app.callback(
    Output(component_id='my-div',component_property='children'),
    [Input(component_id='my-dropdown',component_property='children')]
)
def update_text_output(button_selction):
    return "what the fuck is going on"
'''
