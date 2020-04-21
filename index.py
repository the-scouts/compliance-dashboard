import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# see https://community.plotly.com/t/12463/2
from app import app

from pages.dashboard_generator import DashbordGenerator
from pages.homepage import Homepage

# see https://dash.plot.ly/external-resources to alter the header, footer and favicon
app.index_string = """ 
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Compliance Dashboard Generator - DEVELOPMENT (Adam Turner)</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    # content will be rendered in this element
    html.Div(id='page-content')
])

dg = DashbordGenerator()
dg.set_info("County Team", "October 2019", "Central Yorkshire")
dg.set_people(305, 389)


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/report':
        return dg.get_dashboard()
    else:
        return Homepage()


# @app.callback(Output('output',  'children'), [Input('pop_dropdown', 'value')])
# def update_graph(city):
#     return build_graph(city)


if __name__ == '__main__':
    app.run_server(debug=True)

    dg.set_people(1, 2)
