import pandas as pd
from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc
from datetime import date
from business.objects.option import Option
from business.services.opt_service import OptionsService
from business.services.bs_formula import BS_formula
from business.objects.person import Person
from dateutil.relativedelta import relativedelta
from dash.exceptions import PreventUpdate
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import plotly.express as px
import plotly.graph_objs as go
from plotly.validator_cache import ValidatorCache



def get_relative_maturity(maturity):
    
    maturity = pd.to_datetime(maturity, format="%Y-%m-%d")

    initial_date = date(2023, 12, 8)

    temp_maturity = date(maturity.year, maturity.month, maturity.day)
    rel_maturity = relativedelta(temp_maturity, initial_date)
    rel_maturity = (
        rel_maturity.years + rel_maturity.months / 12.0 + rel_maturity.days / 365.25
    )
    
    return rel_maturity

options = ["Apple", "Amazon", "Ali Baba", "Google", "Meta", "Microsoft", "Sony", "Tesla"]
types=["Put","Call"]

grecques=["Delta","Gamma","Vega","Theta","Rho"]

card_volatility = [
    dbc.CardHeader( 
                   html.H3("Volatilité de l'option", className="card-title"),
),
    dbc.CardBody(
        [
            html.Div(
                id="id_volatility",
                className="card-text",
            ),
            
        ]
    ),
]

card_price = [
    dbc.CardHeader(html.H3("Prix de l'option", className="card-title"),),
    dbc.CardBody(
        [
            html.Div(
                id="id_price",
                className="card-text",
            ),
            
        ]
    ),
]

card_table = [
    dbc.CardHeader(html.H3("Grecques de l'option", className="card-title"),),
    dbc.CardBody(
    html.Table([
        html.Tr([html.Td(["Delta"]), html.Td(id='delta')]),
        html.Tr([html.Td(["Gamma"]), html.Td(id='gamma')]),
        html.Tr([html.Td(["Vega"]), html.Td(id='vega')]),
        html.Tr([html.Td(["Theta"]), html.Td(id='theta')]),
        html.Tr([html.Td(["Rho"]), html.Td(id='rho')]),
    ]),)
    
    ]

card_figure_greek = [
    dbc.CardHeader(html.H3("Graphique des grecques en fonction du sous-jacent", className="card-title"),),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col(html.Div(
                    children=[
                        html.Div(children="Grecques", className="menu-title"),
                        dcc.Dropdown(
                            id="grecque-filter",
                            options=[
                                {"label": grecque, "value": grecque} for grecque in grecques
                            ],
                            value="Delta",
                            style={"height": 40, "width":110, "border-radius": "1em", "border": "3px solid #ccc"},                            
                            clearable=False,
                        ),
                    ]
                )),
                dbc.Col(
                     html.Div(
                    children=[
                        html.Div(children="Min", className="menu-title"),
                        dcc.Input(
                            id="min_S-filter",
                            type="number",
                            value=100,
                            style={"height": 40, "width":110, "border-radius": "1em", "border": "3px solid #ccc"},
                        ),
                    ],
                ),
                ),
                dbc.Col(html.Div(
                    children=[
                        html.Div(children="Max", className="menu-title"),
                        dcc.Input(
                            id="max_S-filter",
                            type="number",
                            value=300,
                            style={"height": 40, "width":110, "border-radius": "1em", "border": "3px solid #ccc"},
                        ),
                    ],
                ),)
                ]),
         
            dcc.Graph(
                        id='greek-graph',
                        figure={}
                    )
            
        ]
    ),
]

card_figure_strike =  [
    dbc.CardHeader(html.H3("Graphique des grecques en fonction du strike", className="card-title"),),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col(html.Div(
                    children=[
                        html.Div(children="Grecques", className="menu-title"),
                        dcc.Dropdown(
                            id="strike_final-filter",
                            options=[
                                {"label": grecque, "value": grecque} for grecque in grecques
                            ],
                            value="Delta",
                            style={"height": 40, "width":110, "border-radius": "1em", "border": "3px solid #ccc"},                            
                            clearable=False,
                        ),
                    ]
                )),
                dbc.Col(
                     html.Div(
                    children=[
                        html.Div(children="Min", className="menu-title"),
                        dcc.Input(
                            id="min_K-filter",
                            type="number",
                            value=100,
                            style={"height": 40, "width":110, "border-radius": "1em", "border": "3px solid #ccc"},
                        ),
                    ],
                ),
                ),
                dbc.Col(html.Div(
                    children=[
                        html.Div(children="Max", className="menu-title"),
                        dcc.Input(
                            id="max_K-filter",
                            type="number",
                            value=300,
                            style={"height": 40, "width":110, "border-radius": "1em", "border": "3px solid #ccc"},
                        ),
                    ],
                ),)
                ]),
         
            dcc.Graph(
                        id='strike_final-graph',
                        figure={}
                    )
            
        ]
    ),
]



app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR],suppress_callback_exceptions=True)

server = app.server

app.layout = dbc.Container(
    [
        html.Div(
                children=[
                    html.P(children="🪙", className="header-emoji"),
                    html.H1(children="Asset Pricing", className="header-title"),
                    html.P(
                        children=(
                            "Dans ce projet, nous mettons en place un outil de pricing d'options selon le modèle de Black-Scholes."
                        ),
                        className="header-description",
                    ),
                ],
                className="header",
            ),
        html.Div(
            [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                    children=[
                        html.Div(children="Option", className="menu-title"),
                        dcc.Dropdown(
                            id="option-filter",
                            options=[
                                {"label": option, "value": option} for option in options
                            ],
                            value="Apple",
                            style={"height": 40, "width":150, "border-radius": "1em", "border": "3px solid #ccc"},                            
                            clearable=False,
                        ),
                    ]
                ),
                    width={"size":3,"offset":2}),
                dbc.Col(
                    html.Div(
                    children=[
                        html.Div(children="Type", className="menu-title"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=[
                                {
                                    "label": type,
                                    "value": type,
                                }
                                for type in types
                            ],
                            value="Call",
                            style={"height": 40, "width":150,  "border-radius": "1em", "border": "3px solid #ccc"},
                            clearable=False,
                            searchable=False,
                            
                        ),
                    ],
                ),
                    width={"size":3}
                    ),
                dbc.Col(
                    html.Div(
                    children=[
                        html.Div(children="Maturité", className="menu-title"),
                        dcc.DatePickerSingle(
                            id="date",
                            min_date_allowed=date(2023,12,10),
                            max_date_allowed=date(2030,12,31),
                            initial_visible_month=date(2023,12,10),
                            date=date(2024,12,8),
                            style={ "border-radius": "1em", "border": "3px solid #ccc"}
                        ),
                    ]
                ),
                    width={"size":3}
                    ),
                
            ]
            ),
        dbc.Row(
            [
                dbc.Col(                
                    html.Div(
                    children=[
                        html.Div(children="S0", className="menu-title"),
                        dcc.Input(
                            id="s0-filter",
                            type="number",
                            style={"height": 40, "width":150, "border-radius": "1em", "border": "3px solid #ccc"},
                        ),
                    ],

                ),
                    width={"size":3,"offset":2}
                    ),
                dbc.Col(
                    html.Div(
                    children=[
                        html.Div(children="Strike", className="menu-title"),
                        dcc.Input(
                            id="strike-filter",
                            type="number",
                            value=100,
                            style={"height": 40, "width":150, "border-radius": "1em", "border": "3px solid #ccc"},
                            className="dropdown",
                        ),
                    ],

                ),
                    width={"size":3}
                    ),
                dbc.Col(
                    html.Div(
                    children=[
                        html.Div(children="Rate", className="menu-title"),
                        dcc.Input(
                            id="rate-filter",
                            type="number",
                            value=0.052,
                            style={"height": 40, "width":130, "border-radius": "1em", "border": "3px solid #ccc", "margin-bottom": 10},
                            className="dropdown",
                        ),
                    ],

                ),
                    width={"size":3}
                    ),
            ],
        ),
            ],
            className="menu",
),
        
        dbc.Row(
            [
                #two graphs here in two columns
                dbc.Col([dbc.Card(card_volatility, color="white", inverse=False,outline=False)
                    ,dbc.Card(card_price, color="white", inverse=False,outline=False)]
                        ,width={"size":5,"offset":1}),

                
                dbc.Col(dbc.Card(
                    card_table
                    , color="white", inverse=False,outline=False),
                        ),
            ]
            ,justify="around",
            style={"margin-top": 10},),
        dbc.Row(
            [
                #two graphs here in two columns
                dbc.Col([dbc.Card(card_figure_greek, color="white", inverse=False,outline=False)
                    ]
                        ,width={"size":5,"offset":1}),

                
                dbc.Col(dbc.Card(
                    card_figure_strike
                    , color="white", inverse=False,outline=False),
                        ),
            ]
            ,justify="around",
            style={"margin-top": 10},),
        dbc.Row(
            [
                dbc.Col(html.Div(
                    children=[
                        html.Div(children="Volatilité implicite", className="menu-title"),
                        dcc.Graph(
                        id='volatility_implicite-graph',
                        figure={}
                    ),
                    ]
                ),
                    width={"size":12}
                    ),
            ]),
        
    ],fluid=True    
)

@app.callback(
    Output("s0-filter", "value"),
    Input("option-filter", "value"),
    Input("type-filter", "value"),
)
def update_s0(option, types):
    """
    This function take the option and the type and return the price of the underlying asset

    Args:
        option (string): option name
        types (string): call or put

    Returns:
        float: price of the market of the underlying asset
    """
    O=Option(option,K=None,T=None)
    return  O.S0

#callback for the volatility take the option and the type and return the volatility

@app.callback(
    Output("id_volatility", "children"),
    # Output("id_price", "children"),
    # Output('delta', 'children'),
    # Output('gamma', 'children'),
    # Output('vega', 'children'),
    # Output('theta', 'children'),
    # Output('rho', 'children'),
    Input("option-filter", "value"),
    Input("type-filter", "value"),
    Input("date", "date"),
    Input("s0-filter", "value"),
    Input("strike-filter", "value"),
    Input("rate-filter", "value"),
    
)
def update_volatility(option, types, date, s0, strike, rate):
    """
    This function take the option, the type, the date, the s0, the strike and the rate and return the volatility
    Args:
        option (string): option name
        types (string): call or put
        date (string): date of maturity
        s0 (string): price of the underlying asset
        strike (_type_): strike price
        rate (_type_): risk free rate

    Raises:
        PreventUpdate: prevent update

    Returns:
        float: volatility
    """
    
    if s0 is None or strike is None or rate is None:
        raise PreventUpdate
    else:
        O=Option(option,K=strike,T=get_relative_maturity(date),r=rate)
        #print(O.name,O.K,O.T,O.r)
        P=Person(types)
        opt_service=OptionsService()
        #print("Options Data:")
        sigma=opt_service.calcul_impl_volatility(O,P)
        # bsm = BS_formula( O, P,sigma)
        # price = f"{bsm.BS_price()[0]:.2f} €"
        # delta=f"{bsm.BS_delta()[0]:.2f}"
        # gamma=f"{bsm.BS_gamma()[0]:.2f}"
        # vega=f"{bsm.BS_vega()[0]:.2f}"
        # theta=f"{bsm.BS_theta()[0]:.2f}"
        # rho=f"{bsm.BS_rho()[0]:.2f}"
        
        return round(sigma[0],2)
# Callback for the price take the option , the type and the sigma and return the price and the greeks

@app.callback(
    Output("id_price", "children"),
    Output('delta', 'children'),
    Output('gamma', 'children'),
    Output('vega', 'children'),
    Output('theta', 'children'),
    Output('rho', 'children'),
    Input("option-filter", "value"),
    Input("type-filter", "value"),
    Input("date", "date"),
    Input("s0-filter", "value"),
    Input("strike-filter", "value"),
    Input("rate-filter", "value"),
    Input("id_volatility", "children"),
)
def update_price(option, types, date, s0, strike, rate, sigma):
    """_summary_

    Args:
        option (str): option name
        types (str): call or put
        date (date):    date of maturity
        s0 (str):   price of the underlying asset
        strike (int):   strike price
        rate (int):     risk free rate
        sigma (float):  volatility

    Raises:
        PreventUpdate: prevent update    

    Returns:
        tuple:  price, delta, gamma, vega, theta, rho
    """
    if s0 is None or strike is None or rate is None or sigma is None:
        raise PreventUpdate
    else:
        O=Option(option,K=strike,T=get_relative_maturity(date),r=rate)
        P=Person(types)
        bsm = BS_formula( O, P,sigma=float(sigma))
        price = f"{bsm.BS_price():.2f} €"
        delta=f"{bsm.BS_delta():.2f}"
        gamma=f"{bsm.BS_gamma():.2f}"
        vega=f"{bsm.BS_vega():.2f}"
        theta=f"{bsm.BS_theta():.2f}"
        
        rho=f"{bsm.BS_rho():.2f}"
        
        return price, delta, gamma, vega, theta, rho

# The callback will depend of Option,type, maturity and rate and sigma

@app.callback(
    Output('greek-graph', 'figure'),
    Input("option-filter", "value"),
    Input("type-filter", "value"),
    Input("date", "date"),
    Input("s0-filter", "value"),
    Input("strike-filter", "value"),
    Input("rate-filter", "value"),
    Input("id_volatility", "children"),
    Input("grecque-filter", "value"),
    Input("min_S-filter", "value"),
    Input("max_S-filter", "value"),
)

def update_graph(option, types, date, s0, strike, rate, sigma, grecque,min_S,max_S):
    """
    This function take the option, the type, the date, the s0, the strike and the rate and return the volatility
    Args:
        option (string): option name
        types (string): call or put
        date (string): date of maturity
        s0 (string): price of the underlying asset
        strike (_type_): strike price
        rate (_type_): risk free rate
    """
    if s0 is None or strike is None or rate is None or sigma is None:
        raise PreventUpdate
    else:
        O=Option(option,K=strike,T=get_relative_maturity(date),r=rate)
        T = get_relative_maturity(date)
        d1 = (np.log(O.S0 / O.K) + (O.r + 0.5 * sigma**2) * O.T) / (sigma * np.sqrt(O.T))
        d2 = d1 - sigma * np.sqrt(O.T)

        # Fonction qui calcule les greeks en fonction de S
        def greek(S,grecque):
            d1 = (np.log(S / O.K) + (O.r + 0.5 * sigma**2) * O.T) / (sigma * np.sqrt(O.T))
            d2 = d1 - sigma * np.sqrt(O.T)
            delta = norm.cdf(d1)
            
    
                # Gamma
            gamma = norm.pdf(d1) / (S * sigma * np.sqrt(O.T))
    
                # Vega
            vega = S * norm.pdf(d1) * np.sqrt(O.T)
    
                # Theta
            theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(O.T)) - O.r * O.K * np.exp(-O.r * O.T) * norm.cdf(d2)
    
                # Rho
            rho = O.K * O.T * np.exp(-O.r * O.T) * norm.cdf(d2)
            
            if grecque=="Delta":
                return delta
            elif grecque=="Gamma":
                return gamma
            elif grecque=="Vega":
                return vega
            elif grecque=="Theta":
                return theta
            else: 
                return rho
            
        S = list(range(min_S,max_S))
        greeks = [greek(i,grecque) for i in S]    
            
        # Change the color in red
        fig = go.Figure(data=[go.Scatter(x=S, y=greeks, line=dict(color="red", width=2))])

        return fig
@app.callback(
    Output('strike_final-graph', 'figure'),
    Input("option-filter", "value"),
    Input("type-filter", "value"),
    Input("date", "date"),
    Input("s0-filter", "value"),
    Input("strike-filter", "value"),
    Input("rate-filter", "value"),
    Input("id_volatility", "children"),
    Input("strike_final-filter", "value"),
    Input("min_K-filter", "value"),
    Input("max_K-filter", "value"),
)
def update_strike(option, types, date, s0, strike, rate, sigma, grecque,min_K,max_K):
    """
    This function take the option, the type, the date, the s0, the strike and the rate and return the volatility
    Args:
        option (string): option name
        types (string): call or put
        date (string): date of maturity
        s0 (string): price of the underlying asset
        strike (_type_): strike price
        rate (_type_): risk free rate
    returns:
        figure: graph of the greek in function of the strike
    """

    if s0 is None or strike is None or rate is None or sigma is None:
        raise PreventUpdate
    else:
        O=Option(option,K=strike,T=get_relative_maturity(date),r=rate)
        T = get_relative_maturity(date)
        d1 = (np.log(O.S0 / O.K) + (O.r + 0.5 * sigma**2) * O.T) / (sigma * np.sqrt(O.T))
        d2 = d1 - sigma * np.sqrt(O.T)

        
        # Fonction qui calcule les greeks en fonction de S
        def greek(K,grecque):
            d1 = (np.log(O.S0 / K) + (O.r + 0.5 * sigma**2) * O.T) / (sigma * np.sqrt(O.T))
            d2 = d1 - sigma * np.sqrt(O.T)
            delta = norm.cdf(d1)
            
    
                # Gamma
            gamma = norm.pdf(d1) / (O.S0 * sigma * np.sqrt(O.T))
    
                # Vega
            vega = O.S0 * norm.pdf(d1) * np.sqrt(O.T)
    
                # Theta
            theta = -(O.S0 * norm.pdf(d1) * sigma) / (2 * np.sqrt(O.T)) - O.r * K * np.exp(-O.r * O.T) * norm.cdf(d2)
    
                # Rho
            rho = K * O.T * np.exp(-O.r * O.T) * norm.cdf(d2)
            
            if grecque=="Delta":
                return delta
            elif grecque=="Gamma":
                return gamma
            elif grecque=="Vega":
                return vega
            elif grecque=="Theta":
                return theta
            else: 
                return rho
            
        K = list(range(min_K,max_K))
        greeks = [greek(i,grecque) for i in K]    
            
        
        # Mettre la cour
        fig = go.Figure(data=[go.Scatter(x=K, y=greeks)])
        return fig
    
@app.callback(
    Output('volatility_implicite-graph', 'figure'),
    Input("option-filter", "value"),
    Input("type-filter", "value"),
    Input("date", "date"),
    Input("s0-filter", "value"),
    Input("strike-filter", "value"),
    Input("rate-filter", "value"),
    Input("id_volatility", "children"),
)
def update_volatility_implicite(option, types, date, s0, strike, rate, sigma):
    """ 
    This function take the option, the type, the date, the s0, the strike and the rate and return the volatility
    Args:
        option (string): option name
        types (string): call or put
        date (string): date of maturity
        s0 (string): price of the underlying asset
        strike (_type_): strike price
        rate (_type_): risk free rate
    returns:
        figure: graph of the volatility implicite
    """
    if s0 is None or strike is None or rate is None or sigma is None:
        raise PreventUpdate
    else:
        O=Option(option,K=strike,T=get_relative_maturity(date),r=rate)
        df = pd.read_csv(f'src/data/clean_ListAllOptions{O.name}.csv')
        df['Maturity'] = pd.to_datetime(df['Maturity'], format="%Y-%m-%d")
        df['Maturity'] = df['Maturity'].apply(lambda x: x.strftime('%Y-%m-%d'))
        df['Maturity'] = df['Maturity'].apply(lambda x: get_relative_maturity(x))
        
        #print(df[['Maturity']])
        
    
        
        
        fig = px.scatter_3d(df, x='Strike', y='Maturity', z='implied Volatility')
        
        return fig
        

if __name__ == "__main__":
    app.run_server(debug=True)

