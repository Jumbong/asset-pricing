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

app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR])

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
        
    ],fluid=True    
)

@app.callback(
    Output("s0-filter", "value"),
    Input("option-filter", "value"),
    Input("type-filter", "value"),
)
def update_s0(option, types):
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
    if s0 is None or strike is None or rate is None or sigma is None:
        raise PreventUpdate
    else:
        O=Option(option,K=strike,T=get_relative_maturity(date),r=rate)
        P=Person(types)
        print(sigma)
        
        bsm = BS_formula( O, P,sigma=float(sigma))
        print(bsm.BS_price())
        price = f"{bsm.BS_price():.2f} €"
        print(30*"*")
        print(price)
        delta=f"{bsm.BS_delta():.2f}"
        print(delta)
        gamma=f"{bsm.BS_gamma():.2f}"
        vega=f"{bsm.BS_vega():.2f}"
        theta=f"{bsm.BS_theta():.2f}"
        
        rho=f"{bsm.BS_rho():.2f}"
        
        return price, delta, gamma, vega, theta, rho







if __name__ == "__main__":
    app.run_server(debug=True)

