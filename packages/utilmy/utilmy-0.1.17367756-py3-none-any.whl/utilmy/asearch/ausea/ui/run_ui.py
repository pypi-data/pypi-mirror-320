"""
   ENV vars

      export AISEARCH_AUTH="AUTH0"     --->  with True authentification 
      export AISEARCH_AUTH="NO_AUTH"   --->  Wihtout ANY authentification
      AUTH=None  : Not set --> Very basic authentification


      export AISEARCH_ANSWER="rag"      ### Get real answers

      export AISEARCH_ANSWER="no" or unsert ###      ### Get Mock JSON

      export AISEARCH_ISTEST="1"     ### Local debug mode
    
      ####if AISEARCH_AUTH is set to "AUTH0" then set the following variables ####

      export AUTH0_CLIENT_ID = "xxxx"   ### Auth0 client ID    
      export AUTH0_CLIENT_SECRET = "xxxx"   ### Auth0 client secret
      export AUTH0_DOMAIN = "xxxx"   ### Auth0 domain
      export APP_SECRET_KEY = "xxxx"   ### App secret key
      export BASE_URL = "http://localhost:8050"   ### Base URL

      values for the following variables already ping in slack under under temp-edge-ai-rag-search-chat-dev channel
      create .env file in the ui folder and add the above variables to it

      deployment file can find under ui/config/adeploy/aigensearch folder and readme file can find under ui/config/adeploy/aigensearch/README.md
      
   
   
   cd ui
   python ui/run_ui.py



    TODO:
       https://tarekraafat.github.io/autoComplete.js/#/configuration?id=cache-optional





"""

if 'import':
    import os, sys, re, json, requests, logging, traceback, random
    from uuid import uuid4
    import diskcache, pandas as pd
    from functools import wraps
    from flask import session, redirect, url_for

    from dotenv import load_dotenv

    from urllib.parse import quote_plus, urlencode
    from utilmy import json_save, date_now, log

    ##### Web Interface ########################################
    import dash
    from dash.dependencies import ALL
    from dash import Input, Output, State, dcc, html, DiskcacheManager, callback_context
    from templateManager import json_to_html
    import dash_dangerously_set_inner_html as dhtml

    # Import JWTManager from flask_jwt_extended
    from jose import jwt as jose_jwt
    from flask_cors import CORS
    import dash_auth
    ####### Local Import
    from component.auth.auth import setup_auth, setup_CORS
    from component.routes.auth_routes import setup_auth_routes
    from component.searchbox import search_box
    from authlib.integrations.flask_client import OAuth

    ####### NAME_FILE = 'data.log' ############################
    import platform
    import dash_loading_spinners as dls
    import time  # Used to simulate a delay
    from dash import callback_context as ctx
    from utilmy import diskcache_load, diskcache_decorator
    from utilmy import date_now
    from test import get_answer_test

    ### check the local
    # from ui.utils.utilmy_base import date_now


if "######## Init ENV, Cache #################################################":
    # Configure logging
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    os_name = platform.system().lower()
    if 'linux' in os_name:
        DIRLOG = "./ztmp/chat_log/ui"
    else:
        DIRLOG = "./ztmp/chat_log/ui"
    log("log", DIRLOG)

    global istest
    istest = 1 if os.environ.get('AISEARCH_ISTEST', "0") == "1" else 0


if "######## Init cache ######################################################":
    launch_uid = uuid4()
    cache = diskcache.Cache("./ztmp/zcache/ui_cache")

    # Background callbacks require a cache manager
    background_callback_manager = DiskcacheManager(
        cache, cache_by=[lambda: launch_uid], expire=60,
    )

    os.environ['CACHE_ENABLE'] = "0"
    os.environ['CACHE_DIR']    = "ztmp/cache/mycache2"
    os.environ['CACHE_TTL']    = "139000"
    os.environ['CACHE_SIZE']   = "1000000000"
    os.environ['CACHE_DEBUG']  = "0"


if '####### html_component ###################################################':
    external_stylesheets = [
        "https://zuu-edge.imgix.net/shared/fonts/Gilroy.css",
        "https://fonts.googleapis.com/icon?family=Material+Icons",

        'https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css',

    ]

    external_scripts = [
        'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML',
        'https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/2.0.10/clipboard.min.js',
        'https://code.jquery.com/jquery-3.7.0.min.js',

        ### Datatables
        'https://cdn.datatables.net/2.1.8/js/dataTables.min.js',


         ### Highcharts
        'https://code.highcharts.com/dashboards/dashboards.js',
        "https://code.highcharts.com/highcharts.js",
        "https://code.highcharts.com/highcharts-more.js",
        "https://code.highcharts.com/modules/heatmap.js",
        "https://code.highcharts.com/modules/histogram-bellcurve.js",
        "https://code.highcharts.com/modules/exporting.js",
        "https://code.highcharts.com/modules/networkgraph.js",
        "https://code.highcharts.com/modules/accessibility.js",
        "https://code.highcharts.com/modules/sankey.js",
        "https://code.highcharts.com/modules/treemap.js",
        "https://code.highcharts.com/modules/treegraph.js"



    ]

    VALID_USERNAME_PASSWORD_PAIRS = {
        'edgeai': 'slot237',
    }

    public_routes = ['/health']


if '####### page_helper_popup ################################################':
    import dash_bootstrap_components as dbc
    from dash import Input, Output, State, html

    from utilmy import config_load
    #qlist = config_load("ui/templates/questions.yaml")
    #qlist = qlist[0]
    from utils_ui import HELP_TEXT
    # HELP_TEXT = HELP_TEXT
    popup_helper = dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Help AI Search - Beta version"), close_button=True),
            dbc.ModalBody([dcc.Markdown(HELP_TEXT, dangerously_allow_html=True, ), ]),
            dbc.ModalFooter(dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0, )),

        ],
        id="modal-backdrop",
        backdrop="static",
        is_open=False,
        size="xl",
        scrollable=True,
    )


if '####### page_template app main ###########################################':
    # Add hidden DataTable to force loading of dependencies
    import dash_table as dt

    hidden_table = html.Div(dt.DataTable(), style={"display": "none"})

    app = dash.Dash(__name__,
                    external_stylesheets=external_stylesheets,
                    external_scripts=external_scripts,
                    background_callback_manager=background_callback_manager,
                    suppress_callback_exceptions=True)

    app.server.secret_key = os.getenv('APP_SECRET_KEY')
    # app.server.permanent_session_lifetime = timedelta(minutes = 15.0)

    app.layout = html.Div([
        popup_helper,
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),
    ])


    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)

        return decorated_function


    # Dash callback to render page content based on the URL
    @app.callback(Output("page-content", "children"),
                  Input("url", "pathname"))
    def display_page(pathname):
        if 'user' not in session and os.getenv('AISEARCH_AUTH') == 'AUTH0':
            return dcc.Location(href="/login", id="redirect-login")
        if pathname == "/":
            return home_layout
        else:
            return html.Div("404 Page Not Found")


if "####### Route  Health ####################################################":
    @app.server.route('/health')
    def health_check():
        return {"status": "healthy"}, 200


if "####### page_chat_search #################################################":
    def read_json(fdata="ui/static/answers/com_describe/data.json"):
        try:
            with open(fdata, 'r') as fi:
                json_content = fi.read()

            data_dict = json.loads(json_content)
            return data_dict

        except Exception as e:
            log(f"Unexpected error occurred: {e}")
            raise e


    # @diskcache_decorator
    def get_questions_bottom(query):
        if "basic" in query:
            return read_json("ui/static/questions/basic_questions.json")
        else:
            return read_json("ui/static/questions/basic_questions.json")


    #questions_bottom = get_questions_bottom("basic")
    questions_bottom = [] # get_questions_bottom("basic")

    home_layout = html.Div(className="chatRoot", children=[
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(id="modal-title"), close_button=True),
                dbc.ModalBody(id="modal-body"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-alert", className="ms-auto", n_clicks=0)
                ),
            ],
            id="alert_handler",
            is_open=False
        ),
        dcc.Store(id='app-store', data={'current_question': '', 'answer': None, 'suggest_questions': questions_bottom},
                  storage_type="session"),
        html.Div(className="chatContainer", children=[
            html.Div(className="chatSubContainer", children=[
                # Content area with loader
                html.Div(id="content", className="content", children=[
                    html.Div(id="loader-container", className="loaderContainer", children=[
                        html.Div(className="loaders", children=[
                            html.Div(id="loading-message", className="loadingMessage"),
                            dls.Clock(
                                html.Div(id="loader-container", className="loaderDummy", children=[]),
                                color="#435278",
                                speed_multiplier=1.5
                            )
                        ])

                    ]),
                    html.Div(id="chat-output", className="basicContent", children=[
                        html.Div(children=[
                        ])
                    ])
                ]),
                html.Div(className="chatManager", children=[
                    html.Div(className="searchContainer", children=[
                        html.Div(className="searchBox", children=[
                            html.Div(id="error-message", className="error-message", style={"display": "none"}),
                            dcc.Textarea(id="user-input", placeholder="Ask questions", className="searchTextBox", rows=2),
                            html.Div(className="searchButtonContainer", children=[
                                html.Div(className="commentContainer", children=[
                                    html.Div("Comments", className="label"),
                                    html.Div(dcc.Textarea(id='comment_input', className='commentBox')),


                                    html.Div(className="actionButtonContainer", children=[
                                        html.Button(id="thumbs-up", className="thumbs", children=[
                                            html.Img(src="/assets/icon/thumbs-up.svg", alt="thumbsUp", width="20",
                                                     height="20"),
                                        ]),
                                    ]),
                                    html.Div(className="actionButtonContainer", children=[
                                        html.Button(id="thumbs-down", className="thumbs", children=[
                                            html.Img(src="/assets/icon/thumbs-down.svg", alt="thumbsDown", width="20",
                                                     height="20"),
                                        ]),
                                    ]),


                                ]),

                                html.Div(className="actionContainer", children=[
                                    html.Div(className="actionButtonContainer", children=[
                                        html.Button(id="modal-button", className="helpButton", children=[
                                            html.Img(src="/assets/icon/help.svg", alt="help", width="20", height="20"),
                                            html.Div("help", className="help")
                                        ]),
                                    ]),
                                    html.Div([
                                        dcc.Dropdown(id='status-dropdown', value='edge', className="searchSource",
                                                     clearable=False,
                                                     options=[{'label': 'Edge Mode ', 'value': 'edge'},
                                                              {'label': 'GPT Only', 'value': 'gpt'}
                                                              ]
                                                     ),
                                    ]),

                                    # html.Div(className="actionButtonContainer", children=[
                                    #     html.Button(id="thumbs-up", className="thumbs", children=[
                                    #         html.Img(src="/assets/icon/thumbs-up.svg", alt="thumbsUp", width="20",
                                    #                  height="20"),
                                    #     ]),
                                    # ]),
                                    # html.Div(className="actionButtonContainer", children=[
                                    #     html.Button(id="thumbs-down", className="thumbs", children=[
                                    #         html.Img(src="/assets/icon/thumbs-down.svg", alt="thumbsDown", width="20",
                                    #                  height="20"),
                                    #     ]),
                                    # ]),


                                    html.Div(className="actionButtonContainer", children=[
                                        html.Button(id="clear-button", className="cleanButton", children=[
                                            html.Img(src="/assets/icon/trash.svg", alt="clean", width="20", height="20"),
                                            html.Div("Clean", className="moreInfo")
                                        ]),
                                    ]),

                                    html.Div(className="actionButtonContainer", children=[
                                        html.Button(id="copy-button", className="copyButton", children=[
                                            html.Img(src="/assets/icon/all-updates.svg", alt="Copy", width="20",
                                                     height="20")
                                        ]),
                                    ]),

                                    html.Button("Search", id="submit-button", className="searchButton")
                                ])
                            ])
                        ])
                    ]),

                    # Suggestions box
                    html.Div(className="suggestions", children=[
                        html.Div(id="suggestions-container", className="suggestionsContainer", children=[
                            # html.Span("What can I ask?"),
                            html.Div(className="buttonsContainer", children=[
                                html.Button(suggestion, className="button", id={"suggestion-btn": i})
                                for i, suggestion in enumerate(questions_bottom)
                            ]),
                        ])
                    ])
                ]),
            ])
        ]),
    ])


if "####### Action: Pop up HELPER ############################################":
    @app.callback(
        Output("modal-backdrop", "is_open"),
        [Input("modal-button", "n_clicks"), Input("close-modal", "n_clicks")],
        [State("modal-backdrop", "is_open")],
        prevent_initial_call=True
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open


if "####### Action : Answer compute #########################################":
    @app.callback(
        [Output('chat-output', 'children'), Output('loader-container', 'children'),
         Output('user-input', 'value', allow_duplicate=True),
         Output('app-store', 'data', allow_duplicate=True)],
        [Input('submit-button', 'n_clicks')],
        [State('user-input', 'value'), State('chat-output', 'children'),
         State('loader-container', 'loader'), State('user-input', 'value'),
         State('status-dropdown', 'value'),
         State('app-store', 'data')
         ],
        prevent_initial_call=True
    )
    def update_chat_output(submit_clicks, question, children, loader, userInput, sourceval, dstore):
        """
        Handles all the input and output related to chat.
        main input and output ares denote by user-input, chat-output
        app-store used to store intermediate state for different actions
            1. For logs and comment management
            2. Followup Question suggestions based on user inputs.
        """
        global istest
        if submit_clicks > 0:
            try:
                log("#### source_val:", sourceval)
                if not question_isvalid(question):
                    msg_html = "Question seems invalid. Please kindly reformulate."

                #### new with direct HTML
                elif 'gpt' in sourceval or " definition " in question:
                    log("###### GPT mode ##########################")
                    question1 = 'gpt mode @@@' + question
                    meta  = {'answer_type': "gpt"}
                    ddict = get_answer_based_on_source(question1, meta=meta)

                    ## store GPT output to store ################################
                    dstore["current_question"] = question1
                    dstore["answer"] = ddict
                    # dstore["suggest_questions"] = ddict.get("question_list", []) if len(
                    #     ddict.get("question_list", [])) > 0 else questions_bottom
                    dstore["suggest_questions"] = np_add_unqiue(question, dstore["suggest_questions"],topk=10)
                    msg_html = answer_markdown_to_html(ddict)


                else:
                    log("###### Edge mode ########################")
                    ddict = get_answer_based_on_source(question)

                    ## store EDGE output to store ################################
                    dstore["current_question"] = question
                    dstore["answer"] = ddict
                    #dstore["suggest_questions"] = ddict.get("question_list", []) if len(
                    #    ddict.get("question_list", [])) > 0 else questions_bottom
                    dstore["suggest_questions"] = np_add_unqiue(question, dstore["suggest_questions"],topk=10)
                    msg_html = answer_dict_to_html(ddict)

                question_hash = hash_int64(question)
                new_question = html.Div(question, className="question", id=f"suggestion-question-{question_hash}")
                new_children = [new_question, msg_html] + children

                return new_children, '', '', dstore
            except  Exception as e:
                log(e)
                traceback.print_exc()

        return dash.no_update, '', '', dstore


    @app.callback(
        [Output('chat-output', 'children', allow_duplicate=True),
         Output('user-input', 'value', allow_duplicate=True)],
        Input('clear-button', 'n_clicks'),
        [State('user-input', 'value'), State('chat-output', 'children')],
        prevent_initial_call=True
    )
    def action_chat_output(clear_clicks, value, existing_output):
        """
        Handles the clear button click event. If the clear button is clicked, clear the text area and the chat output.
        """
        ctx = callback_context
        if not ctx.triggered:
            return existing_output, dash.no_update
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger == 'clear-button' and clear_clicks > 0:
            return [], ''

        return dash.no_update, dash.no_update


    @app.callback(
        Output('suggestions-container', 'children'),
        Input('app-store', 'data'),
        State('suggestions-container', 'children')
    )
    def check_suggest_questions_change(store_data, current_children):
        suggest_questions = store_data.get('suggest_questions', [])

        return html.Div(className="buttonsContainer", children=[
            html.Button(suggestion, className="button", id={"suggestion-btn": i})
            for i, suggestion in enumerate(suggest_questions)
        ])


    @app.callback(
        Output("user-input", "value"),
        [Input({"suggestion-btn": ALL}, "n_clicks")],
        [State("user-input", "value"), State("app-store", "data")],
        prevent_initial_call=True
    )
    def handle_search(suggestion_clicks, input_value=None, data=None):
        ctx = dash.callback_context
        if not any(suggestion_clicks):
            return ""
        if not ctx.triggered:
            return ""
        store_data = ctx.states.get("app-store.data", None)
        if store_data is None:
            return ""
        suggest_questions = store_data.get("suggest_questions", [])
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if "suggestion-btn" in triggered_id:
            index = int(triggered_id.split('":')[1].split('}')[0])
            return suggest_questions[index]
        return ""


    @app.callback(
        [Output("alert_handler", "is_open"),
         Output("modal-title", "children"),
         Output("modal-body", "children")],
        [Input("thumbs-up", "n_clicks"),
         Input("thumbs-down", "n_clicks"),
         Input("copy-button", "n_clicks"),
         Input("close-alert", "n_clicks")],
        [State("alert_handler", "is_open")]
    )
    def toggle_modal(thumbs_up_clicks, thumbs_down_clicks, copy_button_clicks, close_clicks, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open, None, None

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "thumbs-up":
            return True, "", "Thank for your feedback."
        elif button_id == "thumbs-down":
            return True, "", "Thank you for your feedback."
        elif button_id == "copy-button":
            return True, "", "Answers copied in clipboard."
        elif button_id == "close-alert":
            return False, None, None

        return is_open, None, None


if "####### Action: thumb Up/Down comment ###################################":
    @app.callback(
        Output('comment_input', 'value', allow_duplicate=True),
        Input('thumbs-up', 'n_clicks'),
        State('user-input', 'value'),
        State('chat-output', 'children'),
        State('comment_input', 'value'),
        State('app-store', 'data'),
        prevent_initial_call=True
    )
    def action_thumbs_up(up_clicks, value, existing_output, comment_input, status):
        data = {}
        if up_clicks:
            log("Ok called up", comment_input)
            data['input'] = status['current_question']
            data['output'] = status['answer']
            if existing_output:
                if 'props' in existing_output:
                    data['output'] = existing_output['props']['children']
            data['click_type'] = 'up'
            data['comments'] = comment_input
            save_to_file(data)
            return ''


    @app.callback(
        Output('comment_input', 'value'),
        Input('thumbs-down', 'n_clicks'),
        State('user-input', 'value'),
        State('chat-output', 'children'),
        State('comment_input', 'value'),
        State('app-store', 'data'),
        prevent_initial_call=True
    )
    def action_thumbs_down(down_clicks, value, existing_output, comment_input, status):
        log("Ok called down")
        data = {}
        if down_clicks:
            log("Ok called down", comment_input)
            data['input'] = status['current_question']
            data['output'] = status['answer']
            if existing_output:
                if 'props' in existing_output:
                    data['output'] = existing_output['props']['children']
            data['click_type'] = 'down'
            data['comments'] = comment_input
            save_to_file(data)
            return ''


    def save_to_file(data):
        import awswrangler as wr

        try:
            y, m, d, h = date_now(fmt="%Y-%m-%d-%H").split("-")
            ts = date_now(fmt="%y%m%d_%H%M%S")

            dirout2 = DIRLOG + f"/year={y}/month={m}/day={d}/hour={h}/chatui_{ts}.json"

            if "s3:" in DIRLOG:
                wr.s3.to_json(df=pd.DataFrame([data]), path=dirout2)
                log(dirout2)
            else:
                json_save(data, dirout2)
        except Exception as e:
            log(e)


###################################################################################
if "################ Function: Get Answer ##################################":

    def get_answer_based_on_source(query, meta=None):
        os.environ['CACHE_ENABLE'] = "1"
        if 'nocache' in query:
            os.environ['CACHE_ENABLE'] = "0"

        query = str_remove_extra_spaces(query)
        query = str_remove_extra_linebreaks(query)
        query = query.strip()

        ######## Receive from Answer
        ddict = get_answer(query, meta)
        return ddict


    def answer_dict_to_html(ddict):
        html_path = ddict['html']
        html_content = json_to_html(ddict, html_path)
        msg_html = dhtml.DangerouslySetInnerHTML(html_content)

        return msg_html


    def answer_markdown_to_html(ddict):
        md_text = ddict['html_tags'].get("summary", "")
        # md_text  = dash_extract_text(md_text)

        md_text = "*Source : GPT4* \n\n" + md_text
        msg_html = dcc.Markdown(md_text, className='markdown')

        return msg_html


    def dash_extract_text(children):
        if isinstance(children, dict) and 'props' in children:
            return dash_extract_text(children['props'].get('children', ''))

        elif isinstance(children, list):
            return ''.join([dash_extract_text(child) for child in children])

        elif isinstance(children, str):
            return children
        return ''


    def get_answer_debug(query, meta=None):
        msg = """This library introduces the following features:
        - 🏗️ Pydantic schema definitions for type casting and validations
        - 🧵 Templating of prompts to allow for dynamic content
        """
        return msg * 5


    def get_answer_rag(query, meta=None):
        from rag.rag_summ2 import search_run
        dd = {}
        dd["query_id"] = queryid_get()
        dd["session_id"] = session_id_get()
        dd["userid_id"] = userid_get()

        dd2 = search_run(query=query, meta=dd)

        dd2["query_id"] = dd["query_id"]
        dd2["session_id"] = dd["session_id"]
        dd2["userid_id"] = dd["userid_id"]
        return dd2


    get_answer = get_answer_test


if "################ Function Session ######################################":
    def queryid_get(query="", hmodulo=100000):
        query = str(query).strip()
        dt = date_now(fmt="%y%m%d-%H%M%S")
        htxt = hash_int64(query) % hmodulo  ## identify same query
        dg = random.randint(1000, 9999)  ## concurecny
        id1 = f"{dt}_{htxt}_{dg}"
        return id1


    def session_id_get():
        if os.getenv('AISEARCH_AUTH') == "AUTH0":
            userinfo = session.get('user', {}).get('userinfo', {})
            sid = userinfo.get('sid', 'no_auth_sid')
            return sid
        return "no_auth"


    def userid_get():
        if os.getenv('AISEARCH_AUTH') == "AUTH0":
            userinfo = session.get('user', {}).get('userinfo', {})
            sub = userinfo.get('sub', 'no_auth_sub')
            return sub
        return "no_auth"


if "################ Function Helper ######################################":
    def np_add_unqiue(val, ll, topk=10):
        if val not in ll:
            ll = [val] + ll
        return ll[:topk]


    def str_remove_extra_spaces(text):
        return re.sub(r'\s+', ' ', text.strip())


    def str_remove_extra_linebreaks(text):
        """
            # Example usage
            text = "Line 1\n\n\nLine 2\n  \nLine 3\n\n"
            result = remove_extra_linebreaks(text)
            log(result)
        """
        return re.sub(r'\n\s*\n', '\n', text)


    def question_isvalid(question: str) -> bool:
        if not (8 <= len(question) <= 200):
            return False

        #valid_pattern = re.compile(r'^[a-zA-Z0-9\s?._-]+$')
        #if not valid_pattern.match(question):
        #    return False

        return True


    def hash_int64(xstr: str):
        import xxhash
        return xxhash.xxh64_intdigest(str(xstr), seed=0)


    def markdown_to_html(markdown_text):
        import markdown2
        return markdown2.markdown(markdown_text, extras=['fenced-code-blocks', 'tables', 'break-on-newline'])

#####################################################################################
if __name__ == '__main__':
    load_dotenv()

    ############# Port ####################################################
    port = str(sys.argv[1]) if len(sys.argv) > 1 else os.getenv('UI_PORT', "8050")

    ########### DEBUG ####################################################
    debug = True if os.environ.get("AISEARCH_DEBUG", "1") == "1" else False

    ########### get_answer values ########################################
    if os.environ.get("AISEARCH_ANSWER", "demo") == "rag":
        get_answer = get_answer_rag
    else:
        get_answer = get_answer_test

    ############# AUTH ####################################################
    if os.getenv('AISEARCH_AUTH') == "AUTH0":
        app.server.config['AUTH0_CLIENT_ID'] = os.getenv('AUTH0_CLIENT_ID')
        app.server.config['AUTH0_CLIENT_SECRET'] = os.getenv('AUTH0_CLIENT_SECRET')
        app.server.config['AUTH0_DOMAIN'] = os.getenv('AUTH0_DOMAIN')
        app.server.config['ALLOWED_ORIGINS'] = os.getenv('ALLOWED_ORIGINS')
        oauth = setup_auth(app)
        setup_CORS(app)
        setup_auth_routes(app, oauth)

    elif os.getenv('AISEARCH_AUTH') == "NO_AUTH":
        log("AISEARCH INIT: NO_AUTH")

    else:
        auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS, public_routes=public_routes)

    ############# start ####################################################
    app.run_server(debug=debug, host='0.0.0.0', port=port)
