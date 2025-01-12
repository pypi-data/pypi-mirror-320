from dash import Dash, dcc, html, Input, Output
import random


# Initialize the Dash app
app = Dash(__name__)
import random

def get_response(query):
    # Define a list of responses
    responses = [
        "That's interesting!",
        "Could you tell me more?",
        "I need to think about that.",
        "That's a good question!",
        "I'm not sure, but let's explore it!"
    ]
    
    # Generate a response based on the query
    # You can add more logic here to generate responses dynamically
    if query:
        response = random.choice(responses)
    else:
        response = "Please enter a query."
    
    return response


# Define the layout of the app
app.layout = html.Div([
    html.Div([
        html.H1("Query and Response App", style={'textAlign': 'center', 'color': '#333', 'padding': '20px', 'backgroundColor': '#f8f9fa'}),
        
        # Container for the query and responses
        html.Div([
            # Wrap the input and button in a Flexbox container
            html.Div([
                # Input for the query
                dcc.Input(
                    id='query-input', 
                    type='text', 
                    placeholder='Enter your query',
                    style={
                        'width': 'calc(100% - 120px)',  # Adjust width to make space for the button
                        'padding': '10px',
                        'borderRadius': '5px',
                        'border': '1px solid #ccc',
                        'display': 'inline-block',  # Display inline for side-by-side alignment
                        'marginRight': '10px'  # Space between input and button
                    }
                ),
                
                # Button to submit the query
                html.Button(
                    'Submit', 
                    id='submit-button', 
                    n_clicks=0,
                    style={
                        'display': 'inline-block', 
                        'padding': '10px 20px', 
                        'backgroundColor': 'black', 
                        'color': 'white', 
                        'border': 'none', 
                        'borderRadius': '5px', 
                        'cursor': 'pointer',
                        'width': '100px'  # Fixed width for the button
                    }
                ),
            ], style={'textAlign': 'center', 'display': 'flex', 'alignItems': 'center'}),
            
            # Display the query and responses in the same box
            html.Div(
                id='query-responses-box',
                style={
                    'border': '1px solid #ddd',
                    'borderRadius': '5px',
                    'padding': '20px',
                    'width': '80%',
                    'backgroundColor': '#f1f1f1'
                }
            )
        ], style={'textAlign': 'center'})
    ], style={'maxWidth': '800px', 'margin': '0 auto'})
])
# Define the callback to update the query and responses
@app.callback(
    Output('query-responses-box', 'children'),
    [Input('submit-button', 'n_clicks'),
     Input('query-input', 'value')]
)
def update_output(n_clicks, query):
    if n_clicks > 0:
        # Display the query
        response = get_response(query)
        query_display = html.Div(f"Query: {query}", style={'fontSize': '18px', 'fontWeight': 'bold', 'marginBottom': '10px','textAlign':'left'})
        res_header_display = html.Div("Response:", style={'fontSize': '18px', 'fontWeight': 'bold', 'marginBottom': '10px','textAlign':'left'})
        response = html.Div(response, style={'fontSize': '16px', 'fontWeight': 'bold', 'marginBottom': '10px','textAlign':'left'})
        # Generate a list of random responses
        
        return [query_display] +[res_header_display]+ [response]
    
    return ""

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)


