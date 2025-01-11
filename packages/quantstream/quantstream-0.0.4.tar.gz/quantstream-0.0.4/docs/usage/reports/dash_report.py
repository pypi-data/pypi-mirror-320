import dash
import dash_core_components as dcc
import dash_html_components as html
from selenium import webdriver

def create_dash_app(figures, titles):
    # Create a new Dash app
    app = dash.Dash(__name__)

    # Create a list to hold the Dash components for the figures
    figure_components = []

    # For each figure and title, create a dcc.Graph component and a html.H2 component
    for fig, title in zip(figures, titles):
        figure_components.append(html.H2(title))
        figure_components.append(dcc.Graph(figure=fig))

    # Add the figure components to the app's layout
    app.layout = html.Div(figure_components)

    return app

# Create some example figures and titles
figures = [dict(data=[dict(x=[1, 2, 3], y=[4, 1, 2])]), dict(data=[dict(x=[4, 5, 6], y=[1, 4, 3])])]
titles = ['Figure 1', 'Figure 2']

# Create the Dash app
app = create_dash_app(figures, titles)

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)

# Use Selenium to open the Dash app in a browser and save the page as HTML
driver = webdriver.Firefox()  # Or use another browser driver
driver.get('http://localhost:8050')
html = driver.page_source
with open('output.html', 'w') as f:
    f.write(html)
driver.quit()
