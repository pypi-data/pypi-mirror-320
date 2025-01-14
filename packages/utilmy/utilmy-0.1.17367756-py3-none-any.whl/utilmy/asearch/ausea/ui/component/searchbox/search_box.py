from dash import Dash, html, dcc, callback, Input, Output


def render(app: Dash):
    return html.Div(
        className='search_box_container',
        children=[html.Div(
            className='searchBox',
            children=[html.Div(
                className='search_box_sub_container',
                children=[
                    html.Img(
                        src="/assets/icon/searchBlack.svg",
                        className="search_box_search_image",
                        alt="Search Icon"
                    ),
                    dcc.Input(
                        id="search-input",
                        type="text",
                        placeholder="Search your question",
                        className='search_box_input_field'
                    ),
                    # Close Icon
                    html.Img(
                        src="/assets/icon/circularCloseBlack.svg",
                        id="close-icon",
                        className='search_box_remove_text',
                        alt="Close Icon"
                    )
                ]
            )])])


@callback(
    Output('search-input', 'value'),
    Input('close-icon', 'n_clicks')
)
def clear_search_input(n_clicks):
    if n_clicks:
        return ''
    return None
