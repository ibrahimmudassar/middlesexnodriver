import arrow
import gspread
import pandas as pd
from bs4 import BeautifulSoup
from camoufox.sync_api import Camoufox
from google.oauth2.service_account import Credentials

town_rename = {
    "PTY": "PISCATAWAY",
    "SRV": "SAYREVILLE",
    "WDB": "WOODBRIDGE",
    "N B": "NEW BRUNSWICK",
    "NBR": "NEW BRUNSWICK",
    "EBR": "EAST BRUNSWICK",
    "PA": "PERTH AMBOY",
    "JMB": "JAMESBURG",
    "MNR": "MONROE",
    "MDX": "MIDDLESEX",
}

table = ""

with Camoufox(headless="virtual") as browser:
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://mcrecords.co.middlesex.nj.us/publicsearch1/")

    selector = "body > div.container-fluid.ng-scope > div.ng-isolate-scope > div > div.tab-pane.ng-scope.active > div > div > ul > li:nth-child(2) > a"
    page.wait_for_selector(selector, state="visible")
    page.click(selector)

    selector = "body > div.container-fluid.ng-scope > div.ng-isolate-scope > div > div.tab-pane.ng-scope.active > div > div > div > div.tab-pane.ng-scope.active > form > div:nth-child(1) > div.col-sm-7 > div > ul > li:nth-child(5) > input"
    page.wait_for_selector(selector, state="visible")
    page.click(selector)

    selector = "body > div.container-fluid.ng-scope > div.ng-isolate-scope > div > div.tab-pane.ng-scope.active > div > div > div > div.tab-pane.ng-scope.active > form > div:nth-child(7) > div.col-sm-4 > p > span:nth-child(1) > button"
    page.wait_for_selector(selector, state="visible")
    page.click(selector)

    selector = "body > div.container-fluid.ng-scope > div.ng-isolate-scope > div > div.tab-pane.ng-scope.active > div > div > div > div.tab-pane.ng-scope.active > form > div:nth-child(1) > div.col-sm-2 > button"
    page.wait_for_selector(selector, state="visible")
    page.click(selector)

    selector = "#results > div.col-md-2 > button"
    page.wait_for_selector(selector, state="visible")
    page.click(selector)

    page.wait_for_timeout(3000)

    pages = context.pages

    table = pages[1].content()

    browser.close()

soup = BeautifulSoup(table, "html.parser")

# Step 3: Find the table in the HTML
table = soup.find("table")

# Step 4: Convert the table to a pandas DataFrame
df = pd.read_html(str(table))[0]

addresses = df[["Legal", "Town"]].drop_duplicates(subset="Legal").dropna()
addresses = addresses[~addresses["Legal"].str.upper().str.contains("O-")]
addresses = addresses[~addresses["Legal"].str.upper().str.contains("L-")]
addresses["Town"] = addresses["Town"].replace(town_rename)
addresses["full"] = addresses["Legal"] + " " + addresses["Town"]

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_info(
    {
        "type": "service_account",
        "project_id": "macbatter",
        "private_key_id": "64bb9fd2fb0aebd8d29c69ee1682f03b979281cf",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC1RY9OXvTaGQrW\nbLMZ6m6darqzCTVfa9UpfxI6hFZdXhEDMkHtxgOB6KWvjdkVRCblbD6uUHgPOIV9\njRKsrMlkfAtI2oSJwkvUGYsFq5ZnhyFWjdUdVMWWMZ4lx25GS2xkexpe6GrfCzr3\nTiHnqt5qFg3hEjJDivcbsvrp/1MlKSwNddqIekfa2vQ8O2AoDZ5j5LdHhDoKB+Os\n2DwovpnOvpE1uJGf2LEFWWwHrBjhrGKv+iPQN3FEvZmGEC9fMLx8ls00SkBlTIfD\nMWxaa9XcaBX9JyBDx+uIW6oFKZA/u0a0TQWfpc7gh5rlnUiFDBjffaRwLODzlE91\n3x5tnM3/AgMBAAECggEAT/gP8JMTkePaVB5AJP63LdsX4kP9t8rqjxPwBsC7GRWW\ni8JwM2VXxsfL0FbTnf4i6rOGM4BsdsqImYrS4jqX3iybDdjY/60nprpeCnJYN/P1\nUSnhCr+LK2dYTXJdw8UiXHGygIwoGZ3qtY9ShdFrrYFtPg24/vMfcKjU6MYq+Akj\nlgN4yu/O0zhu7+hmEPjWtQF19vQbCJrb/zXPI6+vJb4HkAFmi5iizBpDYng4Fn/R\nCULbHPE5Wy43n/7/X+3zoZobFmsR08JmVY3BYbcaY0kFP7f2YbfX8EvP7Wv+OyyF\ndlnpbDRNzl0X9vQ1w5jPDWqLhxnBjtcSJ0KM/B+GgQKBgQDhAlD3W7ddNDNj1tMe\nmVbx0VgWettgmdXbWlGLmX9S2t7icD6n4JuetLKlcn0GXR58SZeDoGdZFpXO18ic\nFtOOygOz54PasDkel74y+t0hX8EiM7xmjxHA34rJwQZa2B/fL1Ykpuk68NgY9+zS\ndYylrkoGKoWj+kniB2QRun9GSwKBgQDOPRdwb2mTx5mE/RJ999fmHC52FPbkhIs+\noo3t9fgiEe7dilHnXX4c5f+/9AA6MnTmLYpliWGtQBSkKXmXQku4rlgxYR8CsIFC\nI8N9hZeF7UAqQLqS8aVdKfymhjFFxm59K28Enl7YMr3Couu1dcwSF52mnbncs+/k\nBnPJauTWnQKBgQC/Nwazjz++dzQM7m0vncQjcHJZeEKiT1lMNe8CoYlwUgwDhrvY\nUqotLwZ6T1csZ0oW+TtHYrMxJF5fD0WuUD+tIsQOyPpmiEeiVfYOwN3XFNa+SBUd\nWwwNSmtZlS3fWbeMJWAhea7Opgoe/eJF4BuMWRcTMmOrvHG5IerKniC3DQKBgQCj\nBa9tdOPjqLc1ZEYlxK+oeUZQmKnAYPUggaXnH7MQW1SRUjEDzedOOJA8z0cOuaul\n9wGa2UmYhTrLuO0gH4tzZHzaK4czvQmvmk2A/wSTHMLHo3rXhKPOTM4lY5W3Le9Q\nifCrmfQmuZU+MUJYodC5zGkVtz+fsaxCdsc3w4M4EQKBgQDGciIpvgYATN7Rkj2o\nmPPpVB9UjJofzeJWM5MLkVteyAePCPJlN/M++Jq7+Q58j6isPk0+LSgwqb+ePw/n\nwEv+WYaPClo1SmzSKMjke1iXWEjPKAu2vZwmeGjFTzk8GdvdM1P/XQzXBtkwfs21\njktFBkT+FAEqsORXJDI85yZoqw==\n-----END PRIVATE KEY-----\n",
        "client_email": "yo-777@macbatter.iam.gserviceaccount.com",
        "client_id": "111177294346086501985",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/yo-777%40macbatter.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com",
    },
    scopes=scopes,
)

gc = gspread.authorize(creds)

sht1 = gc.open_by_key("1TCecyjatRUf4DpNlu9ilpH4yzh1tWJbN0Ndob4zddYw").sheet1

sheet_data = sht1.get_all_values()

# the first row is just the names of the columns so separate that out
df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
df["time"] = pd.to_datetime(df["time"])
time_now = arrow.now("US/Eastern").isoformat()
for legal in addresses["full"]:
    if legal not in list(df["address"]):
        sht1.append_row([legal, time_now], table_range="A1:B1")
