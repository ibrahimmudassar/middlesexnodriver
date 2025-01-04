# middlesexnodriver
import nodriver as uc
from bs4 import BeautifulSoup
import pandas as pd

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

async def main():
    browser = await uc.start(sandbox=False)
    page = await browser.get("https://mcrecords.co.middlesex.nj.us/publicsearch1/")

    await page.wait()

    document = await page.select(
        "body > div.container-fluid.ng-scope > div.ng-isolate-scope > div > div.tab-pane.ng-scope.active > div > div > ul > li:nth-child(2) > a"
    )
    await document.click()

    await page.wait()

    lis_pendens = await page.select(
        "body > div.container-fluid.ng-scope > div.ng-isolate-scope > div > div.tab-pane.ng-scope.active > div > div > div > div.tab-pane.ng-scope.active > form > div:nth-child(1) > div.col-sm-7 > div > ul > li:nth-child(5) > input"
    )
    await lis_pendens.click()

    days = await page.select(
        "body > div.container-fluid.ng-scope > div.ng-isolate-scope > div > div.tab-pane.ng-scope.active > div > div > div > div.tab-pane.ng-scope.active > form > div:nth-child(7) > div.col-sm-4 > p > span:nth-child(1) > button"
    )
    await days.click()

    search = await page.select(
        "body > div.container-fluid.ng-scope > div.ng-isolate-scope > div > div.tab-pane.ng-scope.active > div > div > div > div.tab-pane.ng-scope.active > form > div:nth-child(1) > div.col-sm-2 > button"
    )
    await search.click()

    await page.wait()

    results = await page.select("#results > div.col-md-2 > button")
    await results.click()

    await page.wait(7)

    return await browser.tabs[1].get_content()


if __name__ == "__main__":

    # since asyncio.run never worked (for me)
    html = uc.loop().run_until_complete(main())

    soup = BeautifulSoup(html, "html.parser")

    # Step 3: Find the table in the HTML
    table = soup.find("table")

    # Step 4: Convert the table to a pandas DataFrame
    df = pd.read_html(str(table))[0]

    addresses = df[["Legal", "Town"]].drop_duplicates(subset="Legal").dropna()
    addresses = addresses[~addresses["Legal"].str.upper().str.contains("O-")]
    addresses = addresses[~addresses["Legal"].str.upper().str.contains("L-")]
    addresses["Town"] = addresses["Town"].replace(town_rename)
    addresses["full"] = addresses["Legal"] + " " + addresses["Town"]
    print(addresses["full"])
