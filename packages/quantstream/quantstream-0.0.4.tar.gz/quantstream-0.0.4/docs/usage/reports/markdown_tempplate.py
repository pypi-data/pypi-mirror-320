import markdown
import plotly
import os
from jinja2 import Environment, FileSystemLoader

import markdown
from jinja2 import Environment, FileSystemLoader

def generate_static_report(figures, titles, template_file, output_html):
    # Convert Plotly figures to HTML divs
    divs = [plotly.io.to_html(fig, full_html=False) for fig in figures]

    # Zip the divs and titles together
    divs_and_titles = list(zip(divs, titles))

    # Load the Jinja2 template
    template_loader = FileSystemLoader(searchpath="./")
    template_env = Environment(loader=template_loader)
    template = template_env.get_template(template_file)

    # Render the template with the divs and titles
    markdown_content = template.render(divs_and_titles=divs_and_titles)

    # Convert the Markdown to HTML with the 'extras' extension
    html_content = markdown.markdown(markdown_content, extensions=['markdown.extensions.extra'])

    # Write the HTML content to the output file
    with open(output_html, 'w') as f:
        f.write(html_content)

    print(f"HTML report saved to {os.path.abspath(output_html)}")
def main():
    # Create some dummy data
    import plotly.graph_objects as go
    import numpy as np

    x = np.linspace(0, 2 * np.pi, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)

    fig1 = go.Figure(data=go.Scatter(x=x, y=y1))
    fig2 = go.Figure(data=go.Scatter(x=x, y=y2))

    # Generate a static report
    generate_static_report(
        figures=[fig1, fig2],
        titles=["Sine Wave", "Cosine Wave"],
        template_file="markown_template.md",
        output_html="output.html"
    )

if __name__ == "__main__":
    main()
