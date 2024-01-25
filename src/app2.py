import pandas as pd
from dash import Dash, Input, Output, dcc, html, no_update
import dash_bootstrap_components as dbc
from datetime import date
from business.objects.option import Option
from business.services.opt_service import OptionsService
from business.services.bs_formula import BS_formula
from business.services.bs_formula_straddle import BS_formula_Straddle
from business.objects.person import Person
from business.objects.swap import Swap
from business.services.swappricer import SwapPricer

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
directions = ["Pay", "Receive"]
discountindexs = ['SOFR', 'BGCR', 'TGCR']

header = html.Div(
                dbc.Row(
                [
                    dbc.Col(html.Div(children = [
                        dcc.Link("Pricing d'options", href="/page1", className="button")]),
                        width={"size":4}
                        ),
                    dbc.Col(html.Div(children = [
                        dcc.Link("Pricing d'un straddle", href="/page2", className="button")]),
                        width={"size":4}
                        ),
                    dbc.Col(html.Div(children = [
                        dcc.Link("Pricing d'un swap de taux", href="/page3", className="button")]),
                        width={"size":4}
                        )])
)

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

card_volatilities = [
    dbc.CardHeader(html.H3("Volatilités", className="card-title"),),
    dbc.CardBody(
    html.Table([
        html.Tr([html.Td(["Call"]), html.Td(id='id_volatility_call')]),
        html.Tr([html.Td(["Put"]), html.Td(id='id_volatility_put')]),
    ]),)]

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

card_price_str = [
    dbc.CardHeader(html.H3("Prix du straddle", className="card-title"),),
    dbc.CardBody(
        [
            html.Div(
                id="id_price_str",
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

card_table_str = [
    dbc.CardHeader(html.H3("Grecques du straddle", className="card-title"),),
    dbc.CardBody(
    html.Table([
        html.Tr([html.Td(["Delta"]), html.Td(id='delta_str')]),
        html.Tr([html.Td(["Gamma"]), html.Td(id='gamma_str')]),
        html.Tr([html.Td(["Vega"]), html.Td(id='vega_str')]),
    ]),)
    
    ]

card_table_sw = [
    dbc.CardHeader(html.H3("Taux obligataires", className="card-title"),),
    dbc.CardBody(
    html.Table([
        html.Tr([html.Td(["Maturité T1 jambe fixe"]), html.Td(id='discount_t1_fix')]),
        html.Tr([html.Td(["Maturité Tn jambe fixe"]), html.Td(id='discount_tn_fix')]),
        html.Tr([html.Td(["Maturité T1 jambe variable"]), html.Td(id='discount_t1_var')]),
        html.Tr([html.Td(["Maturité Tn jambe variable"]), html.Td(id='discount_tn_var')]),
    ]),)
    
    ]

card_leg_table = [
    dbc.CardHeader(html.H3("Valeur de jambe", className="card-title"),),
    dbc.CardBody(
    html.Table([
        html.Tr([html.Td(["Jambe fixe"]), html.Td(id='pv_fix')]),
        html.Tr([html.Td(["Jambe variable"]), html.Td(id='pv_float')]),
    ]),)
    
    ]


card_price_sw = [
    dbc.CardHeader(html.H3("Prix du swap", className="card-title"),),
    dbc.CardBody(
        [
            html.Div(
                id="id_price_sw",
                className="card-text",
            ),
            
        ]
    ),
]

app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR])

server = app.server

content = html.Div(id="page-content", style={"margin-top": "60px", "padding": "20px"})

app.layout = html.Div([dcc.Location(id="url"), header, content])

def page1_layout():
    return dbc.Container(
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
                        html.Div(children="Sous-jacent", className="menu-title"),
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

def page2_layout():
    return dbc.Container(
    [ 
        html.Div(
                children=[
                    html.P(children="🪙", className="header-emoji"),
                    html.H1(children="Asset Pricing", className="header-title"),
                    html.P(
                        children=(
                            "Nous mettons en place un outil de pricing d'un Straddle selon le modèle de Black-Scholes."
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
                        html.Div(children="Sous-jacent", className="menu-title"),
                        dcc.Dropdown(
                            id="option-filter-str",
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
                        html.Div(children="Strike call", className="menu-title"),
                        dcc.Input(
                            id="strike-call-filter",
                            type="number",
                            value=150,
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
                        html.Div(children="Maturité", className="menu-title"),
                        dcc.DatePickerSingle(
                            id="date-str",
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
                            id="s0-filter-str",
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
                        html.Div(children="Strike put", className="menu-title"),
                        dcc.Input(
                            id="strike-put-filter",
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
                            id="rate-filter-str",
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
                    dbc.Col([dbc.Card(card_volatilities, color="white", inverse=False,outline=False),
                        dbc.Card(card_price_str, color="white", inverse=False,outline=False)]
                            ,width={"size":5,"offset":1}),

                    
                    dbc.Col(dbc.Card(
                        card_table_str
                        , color="white", inverse=False,outline=False),
                            ),
                ]
                ,justify="around",
                style={"margin-top": 10},),
    ],fluid=True    
)

def page3_layout():
    return dbc.Container(
    [ 
        html.Div(
                children=[
                    html.P(children="🪙", className="header-emoji"),
                    html.H1(children="Asset Pricing", className="header-title"),
                    html.P(
                        children=(
                            "Nous mettons en place un outil de pricing d'un Straddle selon le modèle de Black-Scholes."
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
                        html.Div(children="Directions", className="menu-title"),
                        dcc.Dropdown(
                            id="direction",
                            options=[
                                {"label": direction, "value": direction} for direction in directions
                            ],
                            value="Pay",
                            style={"height": 40, "width":150, "border-radius": "1em", "border": "3px solid #ccc"},                            
                            clearable=False,
                        ),
                    ]
                ),
                    width={"size":3, 'offset':2}),
                dbc.Col(
                    html.Div(
                    children=[
                        html.Div(children="Notionnel", className="menu-title"),
                        dcc.Input(
                            id="notionnel",
                            type="number",
                            value=10000,
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
                        html.Div(children="Date de pricing", className="menu-title"),
                        dcc.DatePickerSingle(
                            id="date-pr-sw",
                            min_date_allowed=date(2023,1,1),
                            max_date_allowed=date(2030,12,31),
                            initial_visible_month=date.today(),
                            date=date.today(),
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
                        html.Div(children="Index taux ", className="menu-title"),
                        dcc.Dropdown(
                            id="discountindex",
                            options=[
                                {"label": index, "value": index} for index in discountindexs
                            ],
                            value="SOFR",
                            style={"height": 40, "width":150, "border-radius": "1em", "border": "3px solid #ccc"},                            
                            clearable=False,
                        ),
                    ]
                ),
                    width={"size":3,"offset":2}),

                dbc.Col(
                    html.Div(
                    children=[
                        html.Div(children="Date de valeur", className="menu-title"),
                        dcc.DatePickerSingle(
                            id="val-date-sw",
                            min_date_allowed=date(2024,1,1),
                            max_date_allowed=date(2040,12,31),
                            initial_visible_month=date(2024,6,1),
                            date=date(2024,6,1),
                            style={ "border-radius": "1em", "border": "3px solid #ccc"}
                        ),
                    ]
                ),
                    width={"size":3}
                    ),

                dbc.Col(
                    html.Div(
                    children=[
                        html.Div(children="Maturité", className="menu-title"),
                        dcc.DatePickerSingle(
                            id="date-sw",
                            min_date_allowed=date(2023,12,10),
                            max_date_allowed=date(2060,12,31),
                            initial_visible_month=date(2025,1,1),
                            date=date(2025,1,1),
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
                        html.Div(children="Fréquence de la jambe fixe (mois)", className="menu-title"),
                        dcc.Input(
                            id="fixed_frequency",
                            type="number",
                            value=12,
                            style={"height": 40, "width":150, "border-radius": "1em", "border": "3px solid #ccc", "margin-bottom": 10},
                            className="dropdown",
                        ),
                    ],

                ),
                    width={"size":3,"offset":2}
                    ),
                dbc.Col(                
                    html.Div(
                    children=[
                        html.Div(children="Fréquence de la jambe variable (mois)", className="menu-title"),
                        dcc.Input(
                            id="float_frequency",
                            type="number",
                            value=12,
                            style={"height": 40, "width":150, "border-radius": "1em", "border": "3px solid #ccc", "margin-bottom": 10},
                            className="dropdown",
                        ),
                    ],

                ),
                    width={"size":3}
                    ),
                dbc.Col(
                    html.Div(
                    children=[
                        html.Div(children="Taux fixe", className="menu-title"),
                        dcc.Input(
                            id="fixed_rate_sw",
                            type="number",
                            value=0.052,
                            style={"height": 50, "width":150, "border-radius": "1em", "border": "3px solid #ccc", "margin-bottom": 10},
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
                    
                    dbc.Col(dbc.Card(
                        card_table_sw
                        , color="white", inverse=False,outline=False),
                        width={"size":5,"offset":0},
                            ),
                    dbc.Col([dbc.Card(card_price_sw, color="white", inverse=False,outline=False),
                             dbc.Card(card_leg_table,color="white", inverse=False,outline=False )]
                            ,width={"size":5,"offset":0}),
                ]
                ,justify="around",
                style={"margin-top": 10},),
    ],fluid=True    
)


page1 = page1_layout()
page2 = page2_layout()
page3 = page3_layout()


@app.callback(
    Output("page-content", "children"), 
    Input("url", "pathname"))

def display_page(pathname):
    if pathname is None or pathname == "/":
        pathname = "/page1"
    global path
    path = pathname
    print(f"path: {path}")
    if pathname == "/page1":
        return page1
    elif pathname == "/page2":
        return page2
    elif pathname == "/page3":
        return page3
    else:
        return html.H1("404 - Page not found")


@app.callback(
    Output("s0-filter", "value"),
    Input("option-filter", "value"),
    Input("type-filter", "value"),
)
def update_s0(option, types):
    if path != "/page1":
        return no_update
    else:
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
    
    if path != "/page1":
        return no_update
    else:
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
    if path != "/page1":
        return no_update
    else:
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





#### Callbacks straddle 
@app.callback(
    Output("s0-filter-str", "value"),
    Input("option-filter-str", "value"),
)
def update_s0_str(option):
    if path != "/page2":
        return no_update
    else: 
        O=Option(option,K=None,T=None)
        return O.S0

#callback for the volatility take the option and the type and return the volatility

@app.callback(
    Output("id_volatility_call", "children"),
    Output("id_volatility_put", "children"),
    Input("option-filter-str", "value"),
    Input("date-str", "date"),
    Input("s0-filter-str", "value"),
    Input("strike-call-filter", "value"),
    Input("strike-put-filter", "value"),
    Input("rate-filter-str", "value"),
    
)
def update_volatility_str(option, date, s0, strikec, strikep, rate):
    if path != "/page2":
        return no_update
    else :
        if s0 is None or strikec is None or strikep is None or rate is None:
            raise PreventUpdate
        else:
            C=Option(option,K=strikec,T=get_relative_maturity(date),r=rate)
            P=Option(option,K=strikep,T=get_relative_maturity(date),r=rate)
            Pc=Person("Call")
            Pp=Person("Put")
            opt_service=OptionsService()
            sigmac=opt_service.calcul_impl_volatility(C,Pc)
            sigmap=opt_service.calcul_impl_volatility(P,Pp)
            
            return round(sigmac[0],2), round(sigmap[0],2)
# Callback for the price take the option , the type and the sigma and return the price and the greeks

@app.callback(
    Output("id_price_str", "children"),
    Output('delta_str', 'children'),
    Output('gamma_str', 'children'),
    Output('vega_str', 'children'),
    Input("option-filter-str", "value"),
    Input("date-str", "date"),
    Input("s0-filter-str", "value"),
    Input("strike-call-filter", "value"),
    Input("strike-put-filter", "value"),
    Input("rate-filter-str", "value"),
    Input("id_volatility_call", "children"),
    Input("id_volatility_put", "children"),
)
def update_price_str(option, date, s0, strikec, strikep, rate, sigmac, sigmap):
    if path != "/page2":
        return no_update
    else:
        if s0 is None or strikec is None or strikep is None or rate is None or sigmac is None or sigmap is None:
            raise PreventUpdate
        else:
            C=Option(option,K=strikec,T=get_relative_maturity(date),r=rate)
            P=Option(option,K=strikep,T=get_relative_maturity(date),r=rate)
            Pc=Person("Call")
            Pp=Person("Put")

            print(f"{sigmac}")
            print(f"{sigmap}")
            
            bsm_str = BS_formula_Straddle(C, P, sigmac, sigmap)
            print(bsm_str.BS_price())
            price = f"{bsm_str.BS_price():.2f} €"
            print(30*"*")
            print(price)
            delta=f"{bsm_str.BS_delta():.2f}"
            print(delta)
            gamma=f"{bsm_str.BS_gamma():.2f}"
            vega=f"{bsm_str.BS_vega():.2f}"
            
            return price, delta, gamma, vega




#callback for the volatility take the option and the type and return the volatility
@app.callback(
    Output("discount_t1_fix", "children"),
    Output("discount_tn_fix", "children"),
    Output("discount_t1_var", "children"),
    Output("discount_tn_var", "children"),
    Input("direction", "value"),
    Input("notionnel", "value"),
    Input("date-pr-sw", "date"),
    Input("val-date-sw", "date"),
    Input("date-sw", "date"),
    Input("discountindex", "value"),
    Input("fixed_frequency", "value"),
    Input("float_frequency", "value"),
    Input("fixed_rate_sw", "value"),

)

def update_swap_price(direction, notional, valuationdate, valuedate, maturity, discountindex, fixed_frequency, float_frequency, fixed_rate):
    if path != "/page3":
        return no_update
    else:
        if valuationdate is None or valuedate is None or maturity is None or fixed_frequency is None or float_frequency is None or fixed_rate is None or direction is None or notional is None:
            print("None")
            raise PreventUpdate
        else:
            maturitydate = pd.to_datetime(maturity, format="%Y-%m-%d")
            valuationdate = pd.to_datetime(valuationdate, format="%Y-%m-%d")
            valuedate = pd.to_datetime(valuedate, format="%Y-%m-%d")
            swap = Swap(direction, notional, fixed_rate, maturitydate, valuedate, float_frequency, fixed_frequency)
            swappricer = SwapPricer(swap, valuationdate)
            discountrate1_fix = f'{swappricer.DiscountRate(valuedate, fixed_frequency):.2f}'
            discountraten_fix = f'{swappricer.DiscountRate(maturitydate, fixed_frequency):.2f}'
            discountrate1_var = f'{swappricer.DiscountRate(valuedate, float_frequency):.2f}'
            discountraten_var = f'{swappricer.DiscountRate(maturitydate, float_frequency):.2f}'
            return discountrate1_fix, discountraten_fix, discountrate1_var, discountraten_var


@app.callback(
    Output("id_price_sw", "children"),
    Output("pv_fix", "children"),
    Output("pv_float", "children"),
    Input("direction", "value"),
    Input("notionnel", "value"),
    Input("date-pr-sw", "date"),
    Input("val-date-sw", "date"),
    Input("date-sw", "date"),
    Input("discountindex", "value"),
    Input("fixed_frequency", "value"),
    Input("float_frequency", "value"),
    Input("fixed_rate_sw", "value"),

)

def update_swap_price(direction, notional, valuationdate, valuedate, maturity, discountindex, fixed_frequency, float_frequency, fixed_rate):
    if path != "/page3":
        return no_update
    else:
        if valuationdate is None or valuedate is None or maturity is None or fixed_frequency is None or float_frequency is None or fixed_rate is None or direction is None or notional is None:
            print("None")
            raise PreventUpdate
        else:
            maturitydate = pd.to_datetime(maturity, format="%Y-%m-%d")
            valuationdate = pd.to_datetime(valuationdate, format="%Y-%m-%d")
            swap = Swap(direction, notional, fixed_rate, maturitydate, valuedate, float_frequency, fixed_frequency)
            swappricer = SwapPricer(swap, valuationdate)
            price = f'{-swappricer.swap_price():.2f}'
            fixed_pv = f"{swappricer.LegPV('fixed', notional):.2f}"
            float_pv = f"{swappricer.LegPV('float', notional):.2f}"
            return price, fixed_pv, float_pv



if __name__ == "__main__":
    app.run_server(debug=True)

