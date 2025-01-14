"""

   cd ui
   python ui/app.py


"""
import json
import threading
import time
import dash
import openai
import markdown
import css_inline
from dash import Input, Output, State, dcc, html


from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import login_user, UserMixin




NAME_FILE = 'data.log'
START_UPDATE = False
RESPONSE_TEXT = ""
IS_PROCESSING = False


###############################################################################################
########## HTML page ##########################################################################
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
]

external_scripts = [
    'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML',
    'https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/2.0.10/clipboard.min.js'
]





###############################################################################################
########## Generic page #######################################################################
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])


@app.callback(Output("page-content", "children"),
              Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/login":
        return login_layout
    elif pathname == "/home":
        return home_layout
    else:
        return login_layout








############################################################################################
############ Login page ####################################################################
login_layout = html.Div([
    dbc.Input(id="username", placeholder="Username", type="text"),
    dbc.Input(id="password", placeholder="Password", type="password"),
    dbc.Button("Login", id="login-button", color="primary"),
    html.Div(id="login-output"),
    dcc.Location(id="url", refresh=True)
])



class User(UserMixin):
     def __init__(self, username):
         self.id = username



@app.callback(
    Output("url", "pathname"),
    Output("login-output", "children"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value")
)
def login(n_clicks, username, password):
    if n_clicks:
        if username == "admin" and password == "password":
            user = User(username)
            login_user(user) #### user session
            return "/home", ""
        else:
            return dash.no_update, "Invalid credentials"
    return dash.no_update, dash.no_update














############################################################################################
############ Chat page ####################################################################
home_layout = html.Div([

    html.Div([
        dcc.Textarea(id='user-input', placeholder='Enter your query',   className='textarea'),
        html.Button('Submit', id='submit-button', n_clicks=0,   className='submit-button'),
    ], className='textarea-container'),

    html.Div(id='chat-output', className='chat-output'),
    html.Div([
        html.Button(html.I(className='fas fa-thumbs-up'),   id='thumbs-up',    className='icon-button'),
        html.Button(html.I(className='fas fa-thumbs-down'), id='thumbs-down',  className='icon-button'),
        html.Button(html.I(className='fas fa-copy'),        id='copy-button',  className='icon-button')

    ], className='icon-buttons'),
    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,
        n_intervals=0,
        disabled=True
    )
], className='main')




########## Action ####################################################################
def background_task(query):
    global START_UPDATE, RESPONSE_TEXT, IS_PROCESSING
    #time.sleep(15)
    RESPONSE_TEXT = get_answer(query)
    START_UPDATE = False
    IS_PROCESSING = False

def extract_text(children):
    if isinstance(children, dict) and 'props' in children:
        return extract_text(children['props'].get('children', ''))

    elif isinstance(children, list):
        return ''.join([extract_text(child) for child in children])

    elif isinstance(children, str):
        return children
    return ''



@app.callback(
    [Output('chat-output', 'children'),
    Output('interval-component', 'disabled')]
    ,
    [Input('submit-button', 'n_clicks'), Input('interval-component', 'n_intervals')],
    State('user-input', 'value'),
    State('chat-output', 'children')
)
def action_chat_output(submit_clicks, n_intervals, value, existing_output):
    ctx = dash.callback_context
    global START_UPDATE, RESPONSE_TEXT, IS_PROCESSING
    if not ctx.triggered:
        return existing_output, True
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger == 'submit-button' and submit_clicks > 0:
        if not value or value.strip() == "":
            md_text = extract_text(existing_output)
            return dcc.Markdown(md_text , className='markdown'), True
        if not IS_PROCESSING:
            START_UPDATE = True
            IS_PROCESSING = True
            RESPONSE_TEXT = ""
            existing_output = ""
            threading.Thread(target=background_task, args=(value,)).start()
            return dcc.Markdown(existing_output, className='markdown'), False
    elif trigger == 'interval-component' and START_UPDATE:
        existing_content = existing_output or ""
        md_text = extract_text(existing_content)
        return dcc.Markdown(md_text + '.', className='markdown'), False
    if not START_UPDATE and RESPONSE_TEXT:
        return dcc.Markdown(f"Query: {value}\n\n Response: {RESPONSE_TEXT.strip()}", className='markdown'), True

    md_text = extract_text(existing_output)
    return  dcc.Markdown(md_text, className='markdown'), True









##################################################################################
@app.callback(
    Input('thumbs-up', 'n_clicks'),
    State('user-input', 'value'),
    State('chat-output', 'children')
)
def action_thumbs_up(up_clicks, value, existing_output):

    data={}
    if up_clicks:
        print("Ok called up")
        data['input'] = value
        data['output']=''
        if 'props' in existing_output:
            data['output'] = existing_output['props']['children']
        data['click_type'] = 'up'
        save_to_file(data)



@app.callback(
    Input('thumbs-down', 'n_clicks'),
    State('user-input', 'value'),
    State('chat-output', 'children')
)
def action_thumbs_down(down_clicks, value, existing_output):
    data={}
    if down_clicks:
        print("Ok called down")
        data['input'] = value
        data['output'] = ''
        if 'props' in existing_output:
            data['output'] = existing_output['props']['children']
        data['click_type'] = 'down'
        save_to_file(data)


def save_to_file(data):
    with open(NAME_FILE, 'a', encoding='utf-8') as file:
        file.write("\n")
        json.dump(data, file, ensure_ascii=False)










########################################################################################
def get_answer(query):
    msg= """
    # gpt-json
    
    `gpt-json` is a wrapper around GPT that allows for declarative definition of expected output format. Set up a schema, write a prompt, and get results back as beautiful typehinted objects.
    
    This library introduces the following features:
    
    - 🏗️ Pydantic schema definitions for type casting and validations
    - 🧵 Templating of prompts to allow for dynamic content
    - 🔎 Supports Vision API, Function Calling, and standard chat prompts
    - 🚕 Lightweight transformations of the output to fix broken json
    - ♻️ Retry logic for the most common API failures
    - 📋 Predict single-objects and lists of objects
    - ✈️ Lightweight dependencies: only OpenAI, pydantic, and backoff
    
    ## Getting Started
    
    ```bash
    pip install gpt-json
    ```
    
    Here's how to use it to generate a schema for simple tasks:
    
    ```python
    import asyncio
    
    from gpt_json import GPTJSON, GPTMessage, GPTMessageRole
    from pydantic import BaseModel
    
    class SentimentSchema(BaseModel):
        sentiment: str
    
    async def runner():
        gpt_json = GPTJSON[SentimentSchema](API_KEY)
        payload = await gpt_json.run(
            messages=[
                GPTMessage(
                    role=GPTMessageRole.SYSTEM,
                    content=SYSTEM_PROMPT,
                ),
                GPTMessage(
                    role=GPTMessageRole.USER,
                    content="Text: I love this product. It's the best thing ever!",
                )
            ]
        )
        print(payload.response)
        print(f"Detected sentiment: {payload.response.sentiment}")
    
    asyncio.run(runner())    
        
    
    """
    return msg*10









if __name__ == '__main__':
    app.run_server(debug = True)
