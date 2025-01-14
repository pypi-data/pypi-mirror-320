"""

   cd ui
   python ui/run_ui.py


   pip install dash_bootstrap_components



"""
import requests

if 'import':
    import json, threading, time
    from datetime import timedelta
    from uuid import uuid4
    from concurrent.futures import ThreadPoolExecutor, as_completed
#----------------------------------------
    #pip install git+https://github.com/plotly/dash-alternative-viz.git#egg=dash_alternative_vizD
    import dash_alternative_viz as dav
# ----------------------------------------
    import dash, diskcache
    import markdown
    import css_inline
    from dash import Input, Output, State, dcc, html, DiskcacheManager
    import dash_auth
    from dash import Dash, dcc, html, Input, Output, State
    import dash_bootstrap_components as dbc
    from dash.exceptions import PreventUpdate
    from flask_login import login_user, UserMixin

    from utilmy import json_load, json_save, date_now, log
    import dash_dangerously_set_inner_html as dhtml

    # NAME_FILE = 'data.log'
    DIRLOG = "./ztmp/chat_log/ui"
    launch_uid = uuid4()
    cacheUI = diskcache.Cache("./ztmp/zcache/ui_cache")

    # Background callbacks require a cache manager
    background_callback_manager = DiskcacheManager(
        cacheUI, cache_by=[lambda: launch_uid], expire=60,
    )

    from utilmy import os_makedirs

    os_makedirs((DIRLOG))



###############################################################################################
########## HTML page ##########################################################################
if 'html_component':
    external_stylesheets = [
        'https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css',
        'https://codepen.io/chriddyp/pen/bWLwgP.css',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
    ]

    external_scripts = [
        'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML',
        'https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/2.0.10/clipboard.min.js'
    ]

    VALID_USERNAME_PASSWORD_PAIRS = {
        'admin': 'password',
        'a': 'a',

    }

    public_routes = ['/health']
###############################################################################################
########## Generic page #######################################################################
if 'page_template':
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts,
                    background_callback_manager=background_callback_manager,
                    suppress_callback_exceptions=True)
    auth = dash_auth.BasicAuth(
        app,
        VALID_USERNAME_PASSWORD_PAIRS,
        public_routes=public_routes
    )
    app.server.secret_key = 'd176a73e1f8a8b1472f31599a270b41c'
    # app.server.permanent_session_lifetime = timedelta(minutes = 15.0)

    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),

    ])


################Health ####################################
    @app.server.route('/health')
    def health_check():
        return json.dumps({"status": "healthy"}), 200




############################################################################################
############ Login page ####################################################################
if 'page_login':
    login_layout = html.Div([
        dbc.Input(id="username", placeholder="Username", type="text"),
        dbc.Input(id="password", placeholder="Password", type="password"),
        dbc.Button("Login", id="login-button", color="primary"),
        html.Div(id="login-output"),
        dbc.Toast(
            "Invalid credentials. Please try again.",
            id="login-toast",
            is_open=False,
            duration=4000,
        ),
        # dcc.Location(id="url", refresh=False)
    ])


    class User(UserMixin):
        def __init__(self, username):
            self.id = username


    @app.callback(Output("page-content", "children"),
                  Input("url", "pathname"))
    def display_page(pathname):
        # if pathname == "/home":
        return home_layout
        # else:
        #     return login_layout

    #
    #
    # @app.callback(
    #     [Output("url", "pathname"),
    #      Output("login-toast", "is_open")],
    #     [Input("login-button", "n_clicks"),
    #      ],
    #     [State("username", "value"),
    #      State("password", "value"),
    #      State("login-toast", "is_open")]
    # )
    # def update_url_on_login(log_clicks, username, password, is_modal_open):
    #     ctx = dash.callback_context
    #
    #     if not ctx.triggered:
    #         raise PreventUpdate
    #
    #     triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    #
    #     if triggered_id == "login-button" and log_clicks:
    #         if username == "admin" and password == "password":
    #             return "/home", False
    #         else:
    #             return dash.no_update, True
    #     elif triggered_id == "login-toast":
    #         return dash.no_update, not is_modal_open
    #
    #     return dash.no_update, dash.no_update

############################################################################################
############ Chat page ####################################################################
home_layout = html.Div([
    html.Div([
        dcc.Interval(id='interval-component', interval=60000, n_intervals=0),
        dav.HighChart(id='currency-chart', options={}),]
        ),
    dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Modal Window"), close_button=True),
                dbc.ModalBody("""children (a list of or a singular dash component, string or number; optional): The children of this component.

id (string; optional): The ID of this component, used to identify dash components in callbacks. The ID needs to be unique across all of the components in an app.

autoFocus (boolean; optional): DEPRECATED Use autofocus instead Puts the focus on the modal when initialized.

autofocus (boolean; optional): Puts the focus on the modal when initialized.

backdrop (boolean | a value equal to: 'static'; optional): Includes a modal-backdrop element. Alternatively, specify 'static' for a backdrop which doesn't close the modal on click.

backdropClassName (string; optional): DEPRECATED Use backdrop_class_name instead CSS class to apply to the backdrop.

backdrop_class_name (string; optional): CSS class to apply to the backdrop.

centered (boolean; optional): If True, vertically center modal on page.

className (string; optional): DEPRECATED Use class_name instead. Often used with CSS to style elements with common properties.

class_name (string; optional): Often used with CSS to style elements with common properties.

contentClassName (string; optional): DEPRECATED Use content_class_name instead CSS class to apply to the modal content.

content_class_name (string; optional): CSS class to apply to the modal content.

enforceFocus (boolean; optional): When True The modal will prevent focus from leaving the Modal while open.

fade (boolean; optional): Set to False for a modal that simply appears rather than fades into view.

fullscreen (a value equal to: PropTypes.bool, PropTypes.oneOf('sm-down', 'md-down', 'lg-down', 'xl-down', 'xxl-down'); optional): Renders a fullscreen modal. Specifying a breakpoint will render the modal as fullscreen below the breakpoint size.

is_open (boolean; optional): Whether modal is currently open.

keyboard (boolean; optional): Close the modal when escape key is pressed.

labelledBy (string; optional): DEPRECATED Use labelledby instead The ARIA labelledby attribute.

labelledby (string; optional): The ARIA labelledby attribute.

modalClassName (string; optional): DEPRECATED Use modal_class_name instead CSS class to apply to the modal.

modal_class_name (string; optional): CSS class to apply to the modal.

role (string; optional): The ARIA role attribute.

scrollable (boolean; optional): It True, scroll the modal body rather than the entire modal when it is too long to all fit on the screen.

size (string; optional): Set the size of the modal. Options sm, lg, xl for small, large or extra large sized modals, or leave undefined for default size.

style (dict; optional): Defines CSS styles which will override styles previously set.

tag (string; optional): HTML tag to use for the Modal, default: div.

zIndex (number | string; optional): DEPRECATED Use zindex instead Set the z-index of the modal. Default 1050.

zindex (number | string; optional): Set the z-index of the modal. Default 1050.

Keyword arguments for ModalHeader
children (a list of or a singular dash component, string or number; optional): The children of this component.

id (string; optional): The ID of this component, used to identify dash components in callbacks. The ID needs to be unique across all of the components in an app.

className (string; optional): DEPRECATED Use class_name instead. Often used with CSS to style elements with common properties.

class_name (string; optional): Often used with CSS to style elements with common properties.

close_button (boolean; default True): Add a close button to the header that can be used to close the modal.

loading_state (dict; optional): Object that holds the loading state object coming from dash-renderer.

loading_state is a dict with keys:children (a list of or a singular dash component, string or number; optional): The children of this component.

id (string; optional): The ID of this component, used to identify dash components in callbacks. The ID needs to be unique across all of the components in an app.

autoFocus (boolean; optional): DEPRECATED Use autofocus instead Puts the focus on the modal when initialized.

autofocus (boolean; optional): Puts the focus on the modal when initialized.

backdrop (boolean | a value equal to: 'static'; optional): Includes a modal-backdrop element. Alternatively, specify 'static' for a backdrop which doesn't close the modal on click.

backdropClassName (string; optional): DEPRECATED Use backdrop_class_name instead CSS class to apply to the backdrop.

backdrop_class_name (string; optional): CSS class to apply to the backdrop.

centered (boolean; optional): If True, vertically center modal on page.

className (string; optional): DEPRECATED Use class_name instead. Often used with CSS to style elements with common properties.

class_name (string; optional): Often used with CSS to style elements with common properties.

contentClassName (string; optional): DEPRECATED Use content_class_name instead CSS class to apply to the modal content.

content_class_name (string; optional): CSS class to apply to the modal content.

enforceFocus (boolean; optional): When True The modal will prevent focus from leaving the Modal while open.

fade (boolean; optional): Set to False for a modal that simply appears rather than fades into view.

fullscreen (a value equal to: PropTypes.bool, PropTypes.oneOf('sm-down', 'md-down', 'lg-down', 'xl-down', 'xxl-down'); optional): Renders a fullscreen modal. Specifying a breakpoint will render the modal as fullscreen below the breakpoint size.

is_open (boolean; optional): Whether modal is currently open.

keyboard (boolean; optional): Close the modal when escape key is pressed.

labelledBy (string; optional): DEPRECATED Use labelledby instead The ARIA labelledby attribute.

labelledby (string; optional): The ARIA labelledby attribute.

modalClassName (string; optional): DEPRECATED Use modal_class_name instead CSS class to apply to the modal.

modal_class_name (string; optional): CSS class to apply to the modal.

role (string; optional): The ARIA role attribute.

scrollable (boolean; optional): It True, scroll the modal body rather than the entire modal when it is too long to all fit on the screen.

size (string; optional): Set the size of the modal. Options sm, lg, xl for small, large or extra large sized modals, or leave undefined for default size.

style (dict; optional): Defines CSS styles which will override styles previously set.

tag (string; optional): HTML tag to use for the Modal, default: div.

zIndex (number | string; optional): DEPRECATED Use zindex instead Set the z-index of the modal. Default 1050.

zindex (number | string; optional): Set the z-index of the modal. Default 1050.

Keyword arguments for ModalHeader
children (a list of or a singular dash component, string or number; optional): The children of this component.

id (string; optional): The ID of this component, used to identify dash components in callbacks. The ID needs to be unique across all of the components in an app.

className (string; optional): DEPRECATED Use class_name instead. Often used with CSS to style elements with common properties.

class_name (string; optional): Often used with CSS to style elements with common properties.

close_button (boolean; default True): Add a close button to the header that can be used to close the modal.

loading_state (dict; optional): Object that holds the loading state object coming from dash-renderer.

loading_state is a dict with keys:"""),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
                ),
            ],
            id="modal-backdrop",
            backdrop = "static",
            is_open=False,
            size="xl",
            scrollable=True,
            ),

    html.Div([
        html.H4("E"),
        html.Pre("""Example of questions:      
               XXxx



    """)
    ]),

    html.Div([

        dcc.Textarea(id='user-input', placeholder='Enter your question', className='textarea'),
        html.Button('Submit', id='submit-button', n_clicks=0, className='submit-button'),
        html.Button('Clear', id='clear-button', n_clicks=0, className='clear-button'),
        html.Button('Modal', id='modal-button', n_clicks=0, className='clear-button'),

    ], className='textarea-container'),
    html.Div('  ', id='input_dot'),
    html.Div(id='chat-output', className='chat-output'),


    html.Div(dcc.Textarea(id='comment_input', className='comment' )),
    html.Div([
        html.Button(html.I(className='fas fa-thumbs-up'), id='thumbs-up', className='icon-button'),
        html.Button(html.I(className='fas fa-thumbs-down'), id='thumbs-down', className='icon-button'),
        html.Button(html.I(className='fas fa-copy'), id='copy-button', className='icon-button')

    ], className='icon-buttons'),
], className='main')

########## Action #############################################
@app.callback(
    Output('chat-output', 'children', allow_duplicate=True),
    [Input('submit-button', 'n_clicks'),
     Input('clear-button', 'n_clicks')],
    State('user-input', 'value'),
    State('chat-output', 'children'),
    prevent_initial_call=True
)
def action_chat_output(submit_clicks,clear_clicks, value, existing_output):
    ctx = dash.callback_context
    if not ctx.triggered:
        return existing_output

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger == 'clear-button' and clear_clicks > 0:
        return ''


    if trigger == 'submit-button' and submit_clicks > 0:
        if not value or value.strip() == "":
            md_text = existing_output
            # md_text = dash_extract_text(existing_output)
            # return dcc.Markdown(md_text, className='markdown')
            return md_text
        return ''
    return dash.no_update

@app.callback(
    Output('chat-output', 'children'),
    [Input('submit-button', 'n_clicks')],
    State('user-input', 'value'),
    prevent_initial_call=True
)
def update_chat_output(submit_clicks, value):
    if submit_clicks > 0:
        md_text = dash_background_task(value)
        md_text = md_text
        # md_text = dash_extract_text(md_text)
        return md_text
        # return dcc.Markdown(md_text, className='markdown')
    return dash.no_update

def dash_background_task(query):
    time.sleep(5)
    return get_answer(query)


def dash_extract_text(children):
    if isinstance(children, dict) and 'props' in children:
        return dash_extract_text(children['props'].get('children', ''))
    elif isinstance(children, list):
        return ''.join([dash_extract_text(child) for child in children])
    elif isinstance(children, str):
        return children
    return ''


################################################################
@app.callback(
    Output('currency-chart', 'options'),
    Input('interval-component', 'n_intervals')
)
def update_chart(n):
    url = "https://www.highcharts.com/samples/data/usdeur.json"

    response = requests.get(url)

    if response.status_code == 200:
        series_data =response.json()
        chart_options = {
            'chart': {'type': 'area'},  # Тип графика
            'title': {'text': 'Dynamic data from API'},
            'series': [{'name': 'Test', 'data': series_data}]
        }
        return chart_options
    else:
        return {
            'chart': {'type': 'line'},
            'title': {'text': 'Error fetching data'},
            'series': [{'name': 'Error', 'data': []}]
        }

@app.callback(
    Output('comment_input','value', allow_duplicate=True),
    Input('thumbs-up', 'n_clicks'),
    State('user-input', 'value'),
    State('chat-output', 'children'),
    State('comment_input', 'value'),
    prevent_initial_call=True
)
def action_thumbs_up(up_clicks, value, existing_output, comment_input):
    data = {}
    if up_clicks:
        print("Ok called up" , comment_input)
        data['input'] = value
        data['output'] = ''
        if existing_output:
            if 'props' in existing_output:
                data['output'] = existing_output['props']['children']
        data['click_type'] = 'up'
        data['comments'] = comment_input
        save_to_file(data)
        return ''


################################################################
@app.callback(
    Output("modal-backdrop", "is_open"),
    [Input("modal-button", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("modal-backdrop", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
        Output('comment_input','value'),
    Input('thumbs-down', 'n_clicks'),
    State('user-input', 'value'),
    State('chat-output', 'children'),
    State('comment_input', 'value'),
    prevent_initial_call=True
)
def action_thumbs_down(down_clicks, value, existing_output, comment_input):
    data = {}
    if down_clicks:
        print("Ok called down", comment_input)
        data['input'] = value
        data['output'] = ''
        if existing_output:
            if 'props' in existing_output:
                data['output'] = existing_output['props']['children']
        data['click_type'] = 'down'
        data['comments'] = comment_input
        save_to_file(data)
        return ''

def save_to_file(data):
    y, m, d, h = date_now(fmt="%Y-%m-%d-%H").split("-")
    ts = date_now(fmt="%y%m%d_%H%M%S")
    json_save(data, DIRLOG + f"/year={y}/month={m}/day={d}/hour={h}/chatui_{ts}.json")
    # with open(NAME_FILE, 'a', encoding='utf-8') as file:
    #     file.write("\n")
    #     json.dump(data, file, ensure_ascii=False)


########################################################################################
def get_answer_v1(query):
    from rag.rag_summ import search_summarize_with_citation
    try:
        msg = search_summarize_with_citation(query=query, llm_model="gpt-4o-2024-08-06", )
    except Exception as e:
        log(e)
        msg = "Sorry, it took too long..."
    return msg


def get_answer(query):
    class_name_div = 'textarea_h'
    class_name_table = 'textarea_h'
    my_paragraph = 'my-paragraph'
    mess = (
        f"<div class='{class_name_div}'"
        f"    <p class='{my_paragraph}'>This is a paragraph inside a div.</p>"
        f"    <table class='{class_name_table}'>"
        f"        <thead>"
        f"            <tr>"
        f"                <th>Header 1</th>"
        f"                <th>Header 2</th>"
        f"            </tr>"
        f"        </thead>"
        f"        <tbody>"
        f"            <tr>"
        f"                <td>Row 1, Cell 1</td>"
        f"                <td>Row 1, Cell 2</td>"
        f"            </tr>"
        f"            <tr>"
        f"                <td>Row 2, Cell 1</td>"
        f"                <td>Row 2, Cell 2</td>"
        f"            </tr>"
        f"        </tbody>"
        f"    </table>"
        f"</div>")
    return dhtml.DangerouslySetInnerHTML(mess)


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8051)


