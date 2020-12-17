# Ying Tung Lau - sharonlau@brandeis.edu
# Jiaying Yan - jiayingyan@brandeis.edu

# <editor-fold desc="import modules">
import pandas as pd
import numpy as np
import json
import os
import re
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import State, Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from algorithms.Helper import *
from algorithms.LoanImpacts import *

# </editor-fold>

# <editor-fold desc="dash app">
external_stylesheets = [dbc.themes.BOOTSTRAP,
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True


# <editor-fold desc="app-components">
def individiual_contribution_input(index_loan, index_person, style={'display': 'none'}):
    id_contribution_input = {'type': 'contribution', 'index': '-'.join([str(index_loan), index_person])}
    id_individual_contribution = {'type': 'individual-contribution', 'index': '-'.join([str(index_loan), index_person])}
    individual_contribution = dbc.FormGroup(
        [
            dbc.Label("Contributor " + index_person, html_for=id_individual_contribution, className='m-0 d-none'),
            dbc.InputGroup([
                dbc.InputGroupAddon(index_person, addon_type="prepend"),
                dbc.Input(id=id_contribution_input, type="number", min=0, step=0.01, max=1e15,
                          className="border-0", placeholder='0.00'),
                dbc.FormFeedback(valid=False)
            ], className='border-bottom individual-formgroup')

        ], id=id_individual_contribution, style=style, className='input-form-2')
    return individual_contribution


def loan_contribution_input(index_loan, style={'display': 'none'}):
    id_loan_contribution = {'type': 'loan-contribution', 'index': str(index_loan)}
    loan_contribution = html.Div([
        individiual_contribution_input(index_loan, 'A', {'display': 'block'}),
        individiual_contribution_input(index_loan, 'B'),
        individiual_contribution_input(index_loan, 'C')
    ], style=style, id=id_loan_contribution)
    return loan_contribution


def individual_loan_input(index, style={'display': 'none'}):
    id_principal = {'type': 'principal', 'index': str(index)}
    id_rate = {'type': 'rate', 'index': str(index)}
    id_payment = {'type': 'payment', 'index': str(index)}
    id_extra = {'type': 'extra', 'index': str(index)}
    id_group = {'type': 'individual-loan-input', 'index': str(index)}
    loan_header = html.H5('LOAN {}'.format(index), className='card-loan-title')
    principal = dbc.FormGroup(
        [

            dbc.Label("Principal", html_for=id_principal, className='m-0'),
            dbc.InputGroup([
                dbc.InputGroupAddon("$", addon_type="prepend"),
                dbc.Input(id=id_principal, type="number", min=0.01, step=0.01, max=1e15,
                          pattern="re.compile(r'^[1-9]+\d*(\.\d{1,2})?$')", className="border-0"),
                dbc.FormFeedback(valid=False)

            ], className='individual-formgroup border-bottom'),

        ], className='input-form'
    )

    rate = dbc.FormGroup(
        [
            dbc.Label("Interest rate per year", html_for=id_rate, className='m-0'),
            dbc.InputGroup([
                dbc.Input(id=id_rate, type="number", min=0.01, step=0.01, max=1e15, className="border-0"),
                dbc.InputGroupAddon("%", addon_type="prepend"),
                dbc.FormFeedback(valid=False)
            ], className='border-bottom individual-formgroup')

        ], className='input-form'
    )

    payment = dbc.FormGroup(
        [
            dbc.Label("Monthly payment", html_for=id_payment, className='m-0'),
            dbc.InputGroup([
                dbc.InputGroupAddon("$", addon_type="prepend"),
                dbc.Input(id=id_payment, type="number", min=0.01, step=0.01, max=1e15, className="border-0"),
                dbc.FormFeedback(valid=False)
            ], className='border-bottom individual-formgroup')
        ], className='input-form'
    )

    extra = dbc.FormGroup(
        [
            dbc.Label("Extra payment", html_for=id_extra, className='m-0'),
            dbc.InputGroup([
                dbc.InputGroupAddon("$", addon_type="prepend"),
                dbc.Input(id=id_extra, type="number", min=0.0, step=0.01, max=1e15, className="border-0",
                          placeholder='0.00'),
                dbc.FormFeedback(valid=False)
            ], className='border-bottom individual-formgroup')
        ], className='input-form-2'
    )
    contributions = loan_contribution_input(index)

    individual_form = html.Div(
        [loan_header,
         dbc.Form([
             principal,
             rate,
             payment,
             extra,
             contributions
         ])
         ]
        , id=id_group, style=style, className='individual-loan w-100')
    return individual_form


loan_input_card = dbc.Card(
    [
        dbc.CardHeader(
            [
                html.Div(
                    [
                        html.H1('LOAN SPECS'),
                    ],
                    className='w-fit d-flex align-items-center text-nowrap'),
                html.Div(
                    [
                        html.Div(
                            [
                                "Loan Number",
                                html.Div(
                                    [
                                        dbc.Button('-', color='light', id='decrease-loan',
                                                   className='symbol-style offset-2',
                                                   n_clicks=0),
                                        dbc.Button('+', color='light', id='increase-loan',
                                                   className='symbol-style mr-1',
                                                   n_clicks=0),
                                    ], className='increment-btn'),
                            ], className='number-widget pl-3'),
                        html.Div(
                            [
                                'Contribution Number',
                                dbc.Button('+', color='light', id='contribution-button',
                                           className='symbol-style mr-1 increment-btn',
                                           n_clicks=0, ),
                            ], className='number-widget'),
                    ]
                    , className="d-flex flex-column align-items-end"),
            ],
            className='d-inline-flex justify-content-between'),
        dbc.CardBody(
            [
                individual_loan_input(1, {'display': 'block'}),
                individual_loan_input(2),
                individual_loan_input(3),

            ], id="loan-card", className='input-card-body'),
    ], className='input-card'
)


# </editor-fold>


# <editor-fold desc="app-callbacks">

# %% alter input panel
@app.callback(
    [
        Output('loan-number', 'data'),
        Output({'type': 'individual-loan-input', 'index': '2'}, 'style'),
        Output({'type': 'individual-loan-input', 'index': '3'}, 'style'),
        Output({'type': 'loan-contribution', 'index': '1'}, "style"),
        Output({'type': 'loan-contribution', 'index': '2'}, 'style'),
        Output({'type': 'loan-contribution', 'index': '3'}, 'style'),
        Output({'type': 'individual-contribution', 'index': '1-B'}, 'style'),
        Output({'type': 'individual-contribution', 'index': '2-B'}, 'style'),
        Output({'type': 'individual-contribution', 'index': '3-B'}, 'style'),
        Output({'type': 'individual-contribution', 'index': '1-C'}, 'style'),
        Output({'type': 'individual-contribution', 'index': '2-C'}, 'style'),
        Output({'type': 'individual-contribution', 'index': '3-C'}, 'style'),
        Output({'type': 'principal', 'index': '1'}, 'value'),
        Output({'type': 'principal', 'index': '2'}, 'value'),
        Output({'type': 'principal', 'index': '3'}, 'value'),
        Output({'type': 'rate', 'index': '1'}, 'value'),
        Output({'type': 'rate', 'index': '2'}, 'value'),
        Output({'type': 'rate', 'index': '3'}, 'value'),
        Output({'type': 'payment', 'index': '1'}, 'value'),
        Output({'type': 'payment', 'index': '2'}, 'value'),
        Output({'type': 'payment', 'index': '3'}, 'value'),
        Output({'type': 'extra', 'index': '1'}, 'value'),
        Output({'type': 'extra', 'index': '2'}, 'value'),
        Output({'type': 'extra', 'index': '3'}, 'value'),
        Output({'type': 'contribution', 'index': '1-A'}, 'value'),
        Output({'type': 'contribution', 'index': '1-B'}, 'value'),
        Output({'type': 'contribution', 'index': '1-C'}, 'value'),
        Output({'type': 'contribution', 'index': '2-A'}, 'value'),
        Output({'type': 'contribution', 'index': '2-B'}, 'value'),
        Output({'type': 'contribution', 'index': '2-C'}, 'value'),
        Output({'type': 'contribution', 'index': '3-A'}, 'value'),
        Output({'type': 'contribution', 'index': '3-B'}, 'value'),
        Output({'type': 'contribution', 'index': '3-C'}, 'value'),
    ],
    [
        Input("contribution-button", 'n_clicks'),
        Input("decrease-loan", 'n_clicks'),
        Input("increase-loan", 'n_clicks'),
        Input('reset-button', 'n_clicks')
    ],
    [State('loan-number', 'data'),
     State({'type': 'principal', 'index': '1'}, 'value'),
     State({'type': 'principal', 'index': '2'}, 'value'),
     State({'type': 'principal', 'index': '3'}, 'value'),
     State({'type': 'rate', 'index': '1'}, 'value'),
     State({'type': 'rate', 'index': '2'}, 'value'),
     State({'type': 'rate', 'index': '3'}, 'value'),
     State({'type': 'payment', 'index': '1'}, 'value'),
     State({'type': 'payment', 'index': '2'}, 'value'),
     State({'type': 'payment', 'index': '3'}, 'value'),
     State({'type': 'extra', 'index': '1'}, 'value'),
     State({'type': 'extra', 'index': '2'}, 'value'),
     State({'type': 'extra', 'index': '3'}, 'value'),
     State({'type': 'contribution', 'index': '1-A'}, 'value'),
     State({'type': 'contribution', 'index': '1-B'}, 'value'),
     State({'type': 'contribution', 'index': '1-C'}, 'value'),
     State({'type': 'contribution', 'index': '2-A'}, 'value'),
     State({'type': 'contribution', 'index': '2-B'}, 'value'),
     State({'type': 'contribution', 'index': '2-C'}, 'value'),
     State({'type': 'contribution', 'index': '3-A'}, 'value'),
     State({'type': 'contribution', 'index': '3-B'}, 'value'),
     State({'type': 'contribution', 'index': '3-C'}, 'value')]
)
def loan_num(n, back, nxt, reset_n, last_history, principal1, principal2, principal3, rate1, rate2, rate3, payment1,
             payment2, payment3,
             extra1, extra2, extra3, contribution1a, contribution1b, contribution1c, contribution2a, contribution2b,
             contribution2c, contribution3a,
             contribution3b, contribution3c):
    vis = {'display': 'block'}
    invis = {'display': 'none'}
    button_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    reset_n = 0
    if button_id == "reset-button":
        last_history["num"] = 1
        return (last_history,) + tuple({"display": "none"} for i in range(11)) + tuple(None for i in range(21))
    else:
        try:
            if back > last_history["back"]:
                last_history["back"] = back
                last_history['num'] = max(1, last_history['num'] - 1)
            elif nxt > last_history["next"]:
                last_history["next"] = nxt
                last_history['num'] = min(3, last_history['num'] + 1)
            loan_2 = invis
            loan_3 = invis
            contribute_1 = invis
            contribute_2 = invis
            contribute_3 = invis
            contribute_b = invis
            contribute_c = invis
            if n >= 2:
                contribute_b = vis
            if n >= 3:
                contribute_c = vis
            if n:
                contribute_1 = vis
            if last_history['num'] >= 2:
                loan_2 = vis
                if n:
                    contribute_2 = vis
            if last_history['num'] == 3:
                loan_3 = vis
                if n:
                    contribute_3 = vis
            return last_history, loan_2, loan_3, contribute_1, contribute_2, contribute_3, contribute_b, contribute_b, \
                   contribute_b, contribute_c, contribute_c, contribute_c, principal1, principal2, principal3, rate1, rate2, rate3, \
                   payment1, payment2, payment3, extra1, extra2, extra3, contribution1a, contribution1b, contribution1c, \
                   contribution2a, contribution2b, contribution2c, contribution3a, contribution3b, contribution3c
        # if last_history store is None
        except:
            last_history = {"num": 1, "back": 0, "next": 0}
            return (last_history,) + tuple(invis for _ in range(11)) + (
                principal1, principal2, principal3, rate1, rate2, rate3, payment1, payment2, payment3, extra1, extra2,
                extra3, contribution1a, contribution1b, contribution1c, contribution2a, contribution2b, contribution2c,
                contribution3a, contribution3b, contribution3c)


# %%

# %% store input loan data
@app.callback(
    [
        Output('apply-alert', 'children'),
        Output('apply-alert', 'is_open'),
        Output('apply-alert', 'className'),
        Output('go-row-2', 'style'),
        Output('row-2', 'style'),
        Output('row-3', 'style'),
        Output("apply-store", 'data'),
        Output({'type': 'principal', 'index': '1'}, 'invalid'),
        Output({'type': 'rate', 'index': '1'}, 'invalid'),
        Output({'type': 'payment', 'index': '1'}, 'invalid'),
        Output({'type': 'principal', 'index': '2'}, 'invalid'),
        Output({'type': 'rate', 'index': '2'}, 'invalid'),
        Output({'type': 'payment', 'index': '2'}, 'invalid'),
        Output({'type': 'principal', 'index': '3'}, 'invalid'),
        Output({'type': 'rate', 'index': '3'}, 'invalid'),
        Output({'type': 'payment', 'index': '3'}, 'invalid'),
        Output({'type': 'extra', 'index': '1'}, 'invalid'),
        Output({'type': 'extra', 'index': '2'}, 'invalid'),
        Output({'type': 'extra', 'index': '3'}, 'invalid'),
        Output({'type': 'contribution', 'index': '1-A'}, 'invalid'),
        Output({'type': 'contribution', 'index': '1-B'}, 'invalid'),
        Output({'type': 'contribution', 'index': '1-C'}, 'invalid'),
        Output({'type': 'contribution', 'index': '2-A'}, 'invalid'),
        Output({'type': 'contribution', 'index': '2-B'}, 'invalid'),
        Output({'type': 'contribution', 'index': '2-C'}, 'invalid'),
        Output({'type': 'contribution', 'index': '3-A'}, 'invalid'),
        Output({'type': 'contribution', 'index': '3-B'}, 'invalid'),
        Output({'type': 'contribution', 'index': '3-C'}, 'invalid'),
    ],
    [Input('apply-button', 'n_clicks')],
    [
        State('loan-number', 'data'),
        State({'type': 'principal', 'index': '1'}, 'value'),
        State({'type': 'principal', 'index': '2'}, 'value'),
        State({'type': 'principal', 'index': '3'}, 'value'),
        State({'type': 'rate', 'index': '1'}, 'value'),
        State({'type': 'rate', 'index': '2'}, 'value'),
        State({'type': 'rate', 'index': '3'}, 'value'),
        State({'type': 'payment', 'index': '1'}, 'value'),
        State({'type': 'payment', 'index': '2'}, 'value'),
        State({'type': 'payment', 'index': '3'}, 'value'),
        State({'type': 'extra', 'index': '1'}, 'value'),
        State({'type': 'extra', 'index': '2'}, 'value'),
        State({'type': 'extra', 'index': '3'}, 'value'),
        State({'type': 'contribution', 'index': '1-A'}, 'value'),
        State({'type': 'contribution', 'index': '1-B'}, 'value'),
        State({'type': 'contribution', 'index': '1-C'}, 'value'),
        State({'type': 'contribution', 'index': '2-A'}, 'value'),
        State({'type': 'contribution', 'index': '2-B'}, 'value'),
        State({'type': 'contribution', 'index': '2-C'}, 'value'),
        State({'type': 'contribution', 'index': '3-A'}, 'value'),
        State({'type': 'contribution', 'index': '3-B'}, 'value'),
        State({'type': 'contribution', 'index': '3-C'}, 'value'),
        State({'type': 'extra', 'index': '1'}, 'invalid'),
        State({'type': 'extra', 'index': '2'}, 'invalid'),
        State({'type': 'extra', 'index': '3'}, 'invalid'),
        State({'type': 'contribution', 'index': '1-A'}, 'invalid'),
        State({'type': 'contribution', 'index': '1-B'}, 'invalid'),
        State({'type': 'contribution', 'index': '1-C'}, 'invalid'),
        State({'type': 'contribution', 'index': '2-A'}, 'invalid'),
        State({'type': 'contribution', 'index': '2-B'}, 'invalid'),
        State({'type': 'contribution', 'index': '2-C'}, 'invalid'),
        State({'type': 'contribution', 'index': '3-A'}, 'invalid'),
        State({'type': 'contribution', 'index': '3-B'}, 'invalid'),
        State({'type': 'contribution', 'index': '3-C'}, 'invalid'),
    ],
    prevent_initial_call=True)
def on_click(n_clicks, loan_number, principal1, principal2, principal3, rate1, rate2, rate3, payment1,
             payment2, payment3, extra1, extra2, extra3, contribution1a, contribution1b, contribution1c, contribution2a,
             contribution2b, contribution2c, contribution3a, contribution3b, contribution3c, inval1, inval2, inval3,
             inval4, inval5, inval6, inval7, inval8, inval9, inval10, inval11, inval12):
    # reset
    if n_clicks == 0:
        invis = {'display': 'none'}
        return ("", False, "", invis, invis, invis, [],) + tuple(False for i in range(21))

    # check values and store
    else:
        # input value if valid else none
        def num(value):
            try:
                value = float(value)
                if 0.0 < value <= 1e15 and re.compile(r'^[1-9]+\d*(\.\d{1,2})?$').match(str(value)):
                    return value
                else:
                    return None
            except:
                return None

        invalid_flag = [1]

        def extra(value):
            try:
                value = float(value)
                if 0.0 <= value <= 1e15 and (value == 0.0 or re.compile(r'^[1-9]+\d*(\.\d{1,2})?$').match(str(value))):
                    return value
                else:
                    # print(value)
                    invalid_flag[0] = -1
                    return None
            except:
                return None

        # initialize loan data
        loan1, loan2, loan3 = (
            {'principal': '', 'rate': '', 'payment': '', 'extra': '', 'contribution': {'A': '', 'B': '', 'C': ''}}
            for i in range(3))
        loan1['principal'], loan1['rate'], loan1['payment'], loan2['principal'], loan2['rate'], loan2['payment'], loan3[
            'principal'], loan3['rate'], loan3['payment'] = \
            (num(_) for _ in [
                principal1, rate1, payment1,
                principal2, rate2, payment2,
                principal3, rate3, payment3])
        loan1['extra'], loan1['contribution']['A'], loan1['contribution']['B'], loan1['contribution']['C'], \
        loan2['extra'], loan2['contribution']['A'], loan2['contribution']['B'], loan2['contribution']['C'], \
        loan3['extra'], loan3['contribution']['A'], loan3['contribution']['B'], loan3['contribution']['C'] = \
            (extra(_) for _ in [
                extra1, contribution1a, contribution1b, contribution1c,
                extra2, contribution2a, contribution2b, contribution2c,
                extra3, contribution3a, contribution3b, contribution3c])
        # extra = 0 if None
        loan1['extra'], loan1['contribution']['A'], loan1['contribution']['B'], loan1['contribution']['C'], \
        loan2['extra'], loan2['contribution']['A'], loan2['contribution']['B'], loan2['contribution']['C'], \
        loan3['extra'], loan3['contribution']['A'], loan3['contribution']['B'], loan3['contribution']['C'] = \
            (_ or 0 for _ in
             [loan1['extra'], loan1['contribution']['A'], loan1['contribution']['B'], loan1['contribution']['C'],
              loan2['extra'], loan2['contribution']['A'], loan2['contribution']['B'], loan2['contribution']['C'],
              loan3['extra'], loan3['contribution']['A'],
              loan3['contribution']['B'], loan3['contribution']['C']])

        # delete contributor if all extra is 0
        def extra_key_del(extra_key, *args):
            if all(_['contribution'][extra_key] == 0 for _ in args):
                for loan in [loan1, loan2, loan3]:
                    del loan['contribution'][extra_key]

        for _ in ['A', 'B', 'C']:
            extra_key_del(_, loan1, loan2, loan3)

        # update flags for input validation and data
        flags = [not bool(num(_)) for _ in
                 [principal1, rate1, payment1, principal2, rate2, payment2, principal3, rate3, payment3]]
        loan_num = loan_number['num']
        if loan_num == 2:
            loan3 = None
            flags[6:9] = (False for i in range(3))
        if loan_num == 1:
            loan2 = None
            loan3 = None
            flags[3:9] = (False for i in range(6))

        # store data, data = [] if there is invalid input loan
        def is_invalid(loan):
            return not all([loan['principal'], loan['rate'], loan['payment']])

        anchor_style = {'display': 'none'}
        row_display = {'display': 'none'}
        if invalid_flag[0] == -1 or is_invalid(loan1) or (loan_num >= 2 and is_invalid(loan2)) or (
                loan_num == 3 and is_invalid(loan3)):
            data = []

            alert_message = 'Please provide valid loan specs'
            alert_class = 'd-flex apply-alert alert-danger'
        else:
            data = [loan for loan in [loan1, loan2, loan3] if loan]
            for loan in data:
                if loan['payment'] <= loan['principal'] * loan['rate'] / 1200.0:
                    data = []
                    alert_class = 'd-flex apply-alert alert-danger'
                    alert_message = 'Oops! Monthly payment must be greater than interest'
                    break
                else:
                    anchor_style = {'display': 'block'}
                    row_display = {'display': 'flex'}
                    alert_class = 'd-flex apply-alert alert-success'
                    alert_message = 'See your loan schedules below'

        print('loan number is:', loan_num)
        print('stored loan data:', data)
        return (alert_message, True, alert_class, anchor_style, row_display, row_display, data,) + tuple(flags) + (
            inval1, inval2, inval3, inval4, inval5, inval6, inval7, inval8, inval9,
            inval10, inval11, inval12)


# %%

# %% Reset input
@app.callback(
    [Output("contribution-button", 'n_clicks'),
     Output('apply-button', 'n_clicks')],
    [Input('reset-button', 'n_clicks')],
    prevent_initial_call=True)
def reset(n):
    if n:
        return 0, 0


# %%

# %% Show checklist
@app.callback([Output('contribution_checklist', 'options'),
               Output('contribution_checklist', 'value')],
              [Input('apply-store', 'modified_timestamp')],
              [State('apply-store', 'data')],
              prevent_initial_call=True)
def update_checklist(modified_timestamp, loans_data):
    # print(modified_timestamp)
    # print(loans_data)
    loans = loans_data

    if_contribution = any([sum(i.values()) for i in [loan['contribution'] for loan in loans]])
    # Get checklist if having contribution
    if if_contribution:
        contribution = [i['contribution'] for i in loans]
        checklist_options = [{'label': member, 'value': member} for member in contribution[0].keys()]
        checklist_value = list(contribution[0].keys())
    else:
        contribution = None
        checklist_options = []
        checklist_value = []
    return checklist_options, checklist_value


# %% Show schedule figure
# Define functions for use of shedule figure
def get_Bar_principal(index, df_schedule):
    palette = [dict(color='rgba(163, 201, 199, 1)', line=dict(color='rgba(163, 201, 199, 1)')),
               dict(color='rgba(163, 201, 199, 0.7)', line=dict(color='rgba(163, 201, 199, 0.7)')),
               dict(color='rgba(163, 201, 199, 0.4)', line=dict(color='rgba(163, 201, 199, 0.4)')),
               ]
    fig = go.Bar(name='Loan{} Principal'.format(index + 1),
                 x=df_schedule['Payment Number'],
                 y=df_schedule['Applied Principal'],
                 marker=palette[index],
                 legendgroup=index,
                 )
    return fig


def get_Bar_interest(index, df_schedule):
    palette = [dict(color='rgba(236, 197, 76, 1)', line=dict(color='rgba(236, 197, 76, 1)')),
               dict(color='rgba(236, 197, 76, 0.7)', line=dict(color='rgba(236, 197, 76, 0.7)')),
               dict(color='rgba(236, 197, 76, 0.4)', line=dict(color='rgba(236, 197, 76, 0.4)')),
               ]
    fig = go.Bar(name='Loan{} Interest'.format(index + 1),
                 x=df_schedule['Payment Number'],
                 y=df_schedule['Applied Interest'],
                 marker=palette[index],
                 legendgroup=index,
                 )
    return fig


@app.callback([Output('schedule', 'figure'),
               Output('impact_banner', 'children'),
               Output('store_df_impact', 'data'),
               ],
              [Input('contribution_checklist', 'value')],
              [State('apply-store', 'data')],
              prevent_initial_call=True)
def update_schedule_figure(checklist_value, loans_data):
    # print(checklist_value)

    loans = loans_data

    principal = [i['principal'] for i in loans]
    rate = [i['rate'] for i in loans]
    payment = [i['payment'] for i in loans]
    extra_payment = [i['extra'] for i in loans]
    if_contribution = any([sum(i.values()) for i in [loan['contribution'] for loan in loans]])
    if if_contribution:
        contribution = [i['contribution'] for i in loans]
    else:
        contribution = None

    # Compute contribution impact if any
    if contribution != None:
        loan_impacts = LoanImpacts(principal=principal, rate=rate, payment=payment,
                                   extra_payment=extra_payment, contributions=contribution)
        df_impact = loan_impacts.compute_impacts()
        store_df_impact = df_impact.to_json()
    else:
        store_df_impact = ''

    # Get a impact banner according to checklist_value
    # for i in range(len(principal)):
    if contribution != None:
        if len(checklist_value) != 0:
            checklist_value.sort()
            if len(checklist_value) == len(contribution[0]):
                impact_banner = 'With all the contribution, you only need to pay ${} interest in total. The loan term is {}.'.format(
                    *df_impact[df_impact['Index'] == 'ALL'].iloc[0][['InterestPaid', 'Duration']])
            else:
                unchecked_list = [i for i in list(contribution[0].keys()) if i not in checklist_value]
                impact_banner = 'Without the contribution of {}'.format(' and '.join(unchecked_list)) + \
                                ', you need to pay ${} more interest in total. The loan term will be extended by {}.'.format(
                                    *df_impact[df_impact['Index'] == ' and '.join(checklist_value)].iloc[0][
                                        ['MIInterest', 'MIDuration']])
        else:
            impact_banner = 'Without any contribution, you need to pay ${} more interest in total. The loan term will be extended by {}.'.format(
                *df_impact[df_impact['Index'] == 'None'].iloc[0][['MIInterest', 'MIDuration']])
    else:
        impact_banner = None

    # Compute the portfolio schedule according to checklist_value
    loan_portfolio = LoanPortfolio()

    for i in range(len(principal)):
        if contribution != None:
            if len(checklist_value) != 0:
                loan = Loan(principal=principal[i], rate=rate[i],
                            payment=payment[i], extra_payment=extra_payment[i] + sum(
                        [contribution[i][member] for member in checklist_value]))
            else:
                loan = Loan(principal=principal[i], rate=rate[i],
                            payment=payment[i], extra_payment=extra_payment[i])
        else:
            loan = Loan(principal=principal[i], rate=rate[i],
                        payment=payment[i], extra_payment=extra_payment[i])
        loan.check_loan_parameters()
        loan.compute_schedule()
        loan_portfolio.add_loan(loan)

    loan_portfolio.aggregate()

    df_schedules = [Helper.schedule_as_df(loan) for loan in loan_portfolio.loans]

    # Draw schedule plot
    fig = go.Figure(
        data=[get_Bar_principal(index, df_schedule.round(2)) for index, df_schedule in enumerate(df_schedules)] + \
             [get_Bar_interest(index, df_schedule.round(2)) for index, df_schedule in enumerate(df_schedules)]
    )

    fig.update_layout(  # margin={"t": 0, "r": 0.4, "b": 0, "l": 0},  #################
        margin=dict(l=0, r=0, b=0, t=30),
        barmode='stack',
        bargap=0,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title="<b>Schedule</b>", showgrid=False),  # Time to loan termination
        yaxis=dict(title="<b>USD</b>", showgrid=False),
        legend=dict(xanchor='left', x=0 if len(df_schedules) == 3 else 0, y=-0.25, orientation='h'),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(255, 255, 255, 0.9)',
            namelength=-1
        ),
    )

    return fig, impact_banner, store_df_impact


# %% Show contribution
def get_contribution_fig(df_impact):
    fig = go.Figure()
    trace_interest = go.Bar(
        name="Total Interest Paid",
        x=df_impact['Index'],
        y=df_impact['InterestPaid'],
        yaxis='y',
        offsetgroup=1,
        marker=dict(color='rgba(236, 197, 76, 1)')
    )
    trace_duration = go.Bar(
        name="Loan Term",
        x=df_impact['Index'],
        y=df_impact['Duration'],
        yaxis='y2',
        offsetgroup=2,
        marker=dict(color='rgba(163, 161, 161, 1)')
    )
    fig.add_trace(trace_interest)
    fig.add_trace(trace_duration)
    fig['layout'].update(
        margin=dict(l=0, r=0, b=0, t=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(xanchor='left', x=0, y=-0.25, orientation='h'),  # , bordercolor = 'Black', borderwidth = 1
        xaxis=dict(title="<b>Contributor</b>"),
        yaxis=dict(title="<b>Total Interest Paid</b>",
                   range=[0.5 * max(df_impact['InterestPaid']), 1.1 * max(df_impact['InterestPaid'])], showgrid=False),
        yaxis2=dict(title="<b>Loan Term</b>", anchor='x', overlaying='y', side='right', showgrid=False),
    )
    return fig


@app.callback([Output('contribution', 'figure'),
               Output('graph-switch-btn', 'style')],
              [Input('store_df_impact', 'modified_timestamp')],
              [State('store_df_impact', 'data')],
              prevent_initial_call=True)
def contribution_figure(modified_timestamp, store_df_impact):
    if store_df_impact != '':
        df_impact = pd.DataFrame(json.loads(store_df_impact))
        df_impact = df_impact[['Index', 'InterestPaid', 'Duration']]
        df_impact = df_impact[df_impact['Index'].str.contains('and') == False]
        df_impact = df_impact.sort_values('InterestPaid')
        fig = get_contribution_fig(df_impact)
        style = {'display': 'block'}
    else:
        fig = go.Figure()
        style = {'display': 'none'}
    return fig, style


@app.callback([Output('graph-schedule', 'style'),
               Output('contribution', 'style')],
              [Input('graph-switch-btn', 'n_clicks')],
              [State('graph-schedule', 'style'),
               State('contribution', 'style')],
              prevent_initial_call=True)
def figure_switch(n_clicks, schedule_style, contribution_style):
    if n_clicks:
        if schedule_style == {'display': 'none'}:
            schedule_style = {'display': 'flex'}
        else:
            schedule_style = {'display': 'none'}
        if contribution_style == {'display': 'none'}:
            contribution_style = {'display': 'flex'}
        else:
            contribution_style = {'display': 'none'}
        return schedule_style, contribution_style


# %% Schedule Table
@app.callback(
    [
        Output('dropdown_schedule', 'options'),
        Output('dropdown_schedule', 'value')
    ],
    [Input('apply-store', 'modified_timestamp')],
    [State('apply-store', 'data')],
    prevent_initial_call=True)
def choose_loan_to_show_schedule(modified_timestamp, loans_data):
    options = [{'label': 'loan{}'.format(i + 1), 'value': 'loan{}'.format(i + 1)} for i in range(len(loans_data))] + \
              [{'label': 'portfolio', 'value': 'portfolio'}]
    value = 'portfolio'
    return options, value


@app.callback([Output('table_schedule', 'columns'),
               Output('table_schedule', 'data')],
              [Input('apply-store', 'modified_timestamp'),
               Input('dropdown_schedule', 'value')],
              [State('apply-store', 'data')],
              prevent_initial_call=True)
def schedule_table(modified_timestamp, dropdown_value, loans_data):
    columns = ['Payment Number', 'Begin Principal', 'Payment', 'Extra Payment',
               'Applied Principal', 'Applied Interest', 'End Principal']
    columns = [{"name": i, "id": i} for i in columns]

    loans = LoanPortfolio()
    loans_schedule = {}
    for index, loan_data in enumerate(loans_data):
        loan = Loan(principal=loan_data['principal'], rate=loan_data['rate'], payment=loan_data['payment'],
                    extra_payment=loan_data['extra'] + sum(loan_data['contribution'].values()))
        loan.compute_schedule()
        loans.add_loan(loan)
        loans_schedule['loan{}'.format(index + 1)] = Helper.schedule_as_df(loan)
    loans.aggregate()
    loans_schedule['portfolio'] = Helper.schedule_as_df(loans)

    selected_schedule = loans_schedule[dropdown_value].round(2)
    selected_schedule = selected_schedule.to_dict('records')

    return columns, selected_schedule


# %%

# </editor-fold>

# <editor-fold desc="app-layout">

app.layout = html.Div(
    [
        dcc.Store(id="apply-store"),
        dcc.Store(id='loan-number'),
        dcc.Store(id='store_df_impact'),
        dbc.Alert(id='apply-alert', is_open=False, duration=4000, className='apply-alert'),
        dbc.Row(
            [
                html.P('💰', className='bar-title title-icon'),
                html.Div([
                    html.P('MULTI-LOAN CALCULATOR', className='bar-title'),
                    html.P('\u00a0\u00a0\u00a0- by Jiaying Yan, Ying Tung Lau', className='bar-author'),
                ], className='d-flex flex-column align-items-end'),
                dbc.Tooltip(
                    'Need help on loan terminology? Click to see web article on loan amortization by Investopedia.',
                    target='info-button', className='info-tooltip', placement='right', ),
                html.A([dbc.Button(html.I(className="fa fa-question"), className='info-button', color='dark',
                                   outline=True, id='info-button')],
                       href='https://www.investopedia.com/terms/a/amortization_schedule.asp', target='_blank',
                       rel="noopener noreferrer", className='info-button-wrapper'),
            ],
            className='bar'),
        dbc.Row([
            loan_input_card,
            html.Div(
                [
                    html.H1('Multi-loan', className='display-1 m-0 text-nowrap'),
                    html.H1('Calculator', className='display-1 text-nowrap mb-3'),
                    html.P(
                        'Our smart tool helps you manage multiple loans with ease, allowing calculation for '
                        'up to three loans and three contributons.',
                        className='pb-0 pt-3 m-0'),
                    html.P('Enter your loan specs on the left and click submit right now to see your loan schedules!',
                           className='pt-0 pb-2 m-0'),
                    html.Div([
                        dbc.Button("SUBMIT", color="primary", outline=True, id='apply-button', n_clicks=0,
                                   className='apply-button'),
                        dbc.Button('Reset', color='danger', outline=True, id='reset-button', className='reset-button',
                                   n_clicks=0)
                    ], className="apply-btn-group"),

                ],
                className='app-title'),
            html.A(html.I(className="fa fa-chevron-down"), href='#row-2-target', style={'display': 'none'},
                   className='go-row-2', id='go-row-2')
        ], className='app-row-1'),
        dbc.Row(className='blank-row', style={'display': 'none'}),
        dbc.Row(
            [
                html.A(id='row-2-target', className='anchor-target'),
                html.A(html.I(className="fa fa-chevron-up"), href='#top', className='return-to-top'),
                html.Div(
                    [
                        html.H6('Amortization Schedule and Contribution Impact', className='display-4 row-2-title'),
                        html.P(
                            "See the interactive chart for amortization schedule of your loan portforlio. "),
                        html.P(
                            'Receiving contributons for repaying loans? Check or uncheck the contributor boxes to see changes'
                            ' of your loan schedules under different combination of contributions, and compare the impact'
                            ' on total interest and loan term among contributors.'),
                        dbc.Button([html.Span('Switch Chart\u00a0'), html.Span(html.I(className="fa fa-caret-right"))],
                                   id='graph-switch-btn', className='switch-btn', n_clicks=0, color='dark',
                                   outline=True)
                    ], className='row-2-text'),
                html.Div([
                    html.Div(
                        [
                            html.Div(id='impact_banner', className='impact_banner'),
                            dbc.Checklist(id='contribution_checklist'),
                            dcc.Graph(id='schedule', figure=go.Figure(), className='graph-schedule')
                        ], style={'display': 'flex'}, id='graph-schedule', className='graph-schedule-wrapper'
                    ),
                    dcc.Graph(id='contribution', className='graph-contribution', style={'display': 'none'}),

                ], className='graph-container')
            ],
            className='app-row-2', id='row-2', style={'display': 'none'}),
        dbc.Row(className='blank-row', style={'display': 'none'}),
        dbc.Row(
            [
                html.A(id='row-3-target', className='anchor-target'),
                html.A(html.I(className="fa fa-chevron-up"), href='#top', className='return-to-top'),
                html.H6('Amortization Table', className='display-4 row-3-title'),
                html.Div(
                    [
                        dcc.RadioItems(id='dropdown_schedule'),
                        html.Div(dash_table.DataTable(
                            id='table_schedule',
                            style_table={'overflowY': 'auto'},
                            style_cell={'textOverflow': 'ellipsis', },
                            style_header={'bacgroundColor': 'white', 'fontWeight': 'bold'},
                            style_as_list_view=True,
                        ), className="table-wrapper"),

                    ], className='schedule-table-group'),
            ],
            className='app-row-3', id='row-3', style={'display': 'none'}),
    ], className='app-body'
)

app.run_server(debug=False, use_reloader=False)
# </editor-fold>

# </editor-fold>