card_hist_volatility = [
    dbc.CardHeader( 
                   html.H3("Volatilité historique", className="card-title"),
),
    dbc.CardBody(
        [
            html.Div(
                id="hist_volatility",
                className="card-text",
            ),
            
        ]
    ),
]

card_asian_price = [
    dbc.CardHeader(html.H3("Prix de l'option", className="card-title"),),
    dbc.CardBody(
        [
            html.Div(
                id="id_asian_price",
                className="card-text",
            ),
            
        ]
    ),
]

card_asian_table = [
    dbc.CardHeader(html.H3("Grecques de l'option", className="card-title"),),
    dbc.CardBody(
    html.Table([
        html.Tr([html.Td(["Delta"]), html.Td(id='asian_delta')]),
        html.Tr([html.Td(["Gamma"]), html.Td(id='asian_gamma')]),
        html.Tr([html.Td(["Vega"]), html.Td(id='asian_vega')]),
    ]),)
    
    ]

def page4_layout():
    return dbc.Container(
    [   
        html.Div(
                children=[
                    html.P(children="🪙", className="header-emoji"),
                    html.H1(children="Pricing d'options Asiatiques", className="header-title"),
                    html.P(
                        children=(
                            "Sur cette page, nous mettons en place un outil de pricing d'une option asiatique par Monte Carlo en suivant l'équation de Black-Scholes."
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
                            id="option-asian-filter",
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
                            id="type-asian-filter",
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
                        html.Div(children="Fenêtre", className="menu-title"),
                        dcc.Input(
                            id="fen-filter",
                            type="number",
                            value=20,
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
                            id="asian_date",
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
                            id="s0-asian-filter",
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
                            id="strike-asian-filter",
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
                            id="rate-asian-filter",
                            type="number",
                            value=0.052,
                            style={"height": 40, "width":130, "border-radius": "1em", "border": "3px solid #ccc", "margin-bottom": 10},
                            className="dropdown",
                        ),
                    ],

                ),
                    width={"size":3}
                    ),
                dbc.Col(
                    html.Div(
                    children=[
                        html.Div(children="Nombre de simulations", className="menu-title"),
                        dcc.Input(
                            id="n_simul-filter",
                            type="number",
                            value=3000,
                            style={"height": 40, "width":150, "border-radius": "1em", "border": "3px solid #ccc"},
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
                    dbc.Col([dbc.Card(hist_volatility, color="white", inverse=False,outline=False)
                        ,dbc.Card(card_asian_price, color="white", inverse=False,outline=False)]
                            ,width={"size":5,"offset":1}),

                    
                    dbc.Col(dbc.Card(
                        card_asian_table
                        , color="white", inverse=False,outline=False),
                            ),
                ]
                ,justify="around",
                style={"margin-top": 10},),
    ],fluid=True    
)


@app.callback(
    Output("s0-asian-filter", "value"),
    Input("option-asian-filter", "value"),
    Input("type-asian-filter", "value"),
)
def update_s0(option, types):
    if path != "/page4":
        return no_update
    else:
        O=Option(option,K=None,T=None)
        return  O.S0

#callback for the volatility take the option and the type and return the volatility

@app.callback(
    Output("hist_volatility", "children"),
    Input("option-asian-filter", "value"),
    Input("type-aian-filter", "value"),
    Input("asian_date", "date"),
    Input("s0-asian-filter", "value"),
    Input("strike-asian-filter", "value"),
    Input("rate-asian-filter", "value"),
    
)
def update_volatility(option, types, date, s0, strike, rate):
    if path != "/page4":
        return no_update
    else:    
        if s0 is None or strike is None or rate is None:
            raise PreventUpdate
        else:
            O=Option(option,K=strike,T=get_relative_maturity(date),r=rate)
            P=Person(types)
            opt_service=OptionsService()

            hist_sigma=opt_service.calcul_hist_volatility(O,P)
            
            return round(hist_sigma[0],2)


@app.callback(
    Output("id_asian_price", "children"),
    Output('asian_delta', 'children'),
    Output('asian_gamma', 'children'),
    Output('asian_vega', 'children'),
    Input("option-asian-filter", "value"),
    Input("type-asian-filter", "value"),
    Input("asian_date", "date"),
    Input("s0-asian-filter", "value"),
    Input("strike-asian-filter", "value"),
    Input("rate-asian-filter", "value"),
    Input("hist_volatility", "children"),
    Input("n_simul-filter", "value"),
    Input("fen-filter", "value"),
)
def update_price(option, types, date, s0, strike, rate, sigma, n_simul, fen):
    if path != "/page4":
        return no_update
    else:
        if s0 is None or strike is None or rate is None or sigma is None or n_simul is None or fen is None:
            raise PreventUpdate
        else:
            O=Option(option,K=strike,T=get_relative_maturity(date),r=rate)
            P=Person(types)
            
            As_price = AsianMCPricer( O, P,float(sigma), n_simul, fen)
            print(As_price.BS_price())
            price = f"{As_price.MC_price(s0, sigma):.2f} €"
            print(30*"*")
            print(price)
            delta=f"{As_price.MC_delta():.2f}"
            print(delta)
            gamma=f"{As_price.MC_gamma():.2f}"
            vega=f"{As_price.MC_vega():.2f}"
            
            return price, delta, gamma, vega