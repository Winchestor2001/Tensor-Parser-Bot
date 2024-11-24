import json
import uuid

import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

base_url = "https://graphql.tensor.trade/graphql"


def get_slug(nft_name):
    payload = [
        {"operationName": "SolExchangeRate", "variables": {}, "query": "query SolExchangeRate {\n  solExchangeRate\n}"},
        {"operationName": "SolanaTps", "variables": {}, "query": "query SolanaTps {\n  solanaTps\n}"},
        {"operationName": "MpFees", "variables": {},
         "query": "query MpFees($owner: String) {\n  mpFees(owner: $owner) {\n    mp\n    makerFeeBps\n    takerFeeBps\n    takerRoyalties\n    __typename\n  }\n}"},
        {"operationName": "PriorityFees", "variables": {},
         "query": "query PriorityFees {\n  priorityFees {\n    ...ReducedPriorityFees\n    __typename\n  }\n}\n\nfragment ReducedPriorityFees on PriorityFees {\n  medium\n  high\n  veryHigh\n  __typename\n}"},
        {"operationName": "JitoTipFloor", "variables": {},
         "query": "query JitoTipFloor {\n  jitoTipFloor {\n    landedTips25thPercentile\n    __typename\n  }\n}"},
        {"operationName": "RpcProvidersWithRateLimit", "variables": {},
         "query": "query RpcProvidersWithRateLimit {\n  rpcProvidersWithRateLimit {\n    provider\n    rateLimit\n    weight\n    __typename\n  }\n}"},
        {"operationName": "CollectionPointsMultipliers", "variables": {},
         "query": "query CollectionPointsMultipliers {\n  collectionPointsMultipliers {\n    slug\n    multiplier\n    __typename\n  }\n}"},
        {"operationName": "HeaderAnnouncement", "variables": {},
         "query": "query HeaderAnnouncement {\n  headerAnnouncement {\n    msg\n    colorScheme\n    __typename\n  }\n}"},
        {"operationName": "Instrument", "variables": {"slug": nft_name},
         "query": "query Instrument($slug: String!) {\n  instrumentTV2(slug: $slug) {\n    id\n    slug\n    __typename\n  }\n}"},
        {"operationName": "GlobalVol", "variables": {}, "query": "query GlobalVol {\n  globalVol\n}"}
    ]
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": "Python/requests"
    }

    # Send the POST request
    response = requests.post(base_url, json=payload, headers=headers)
    data = response.json()
    slugs = []

    for item in data:
        if "data" in item:
            if "instrumentTV2" in item["data"] and item["data"]["instrumentTV2"]:
                slug = item["data"]["instrumentTV2"].get("slug")
                if slug:
                    slugs.append(slug)

    # Print the extracted slugs
    return slugs[0]


def get_graphql_api(slug):
    payload = [
        {
            "operationName": "CollAnalytics",
            "variables": {
                "slug": slug
            },
            "query": """
            query CollAnalytics($slug: String!) {
              collectionHolderStats(slug: $slug) {
                uniqueHolders
                topHolders {
                  ...CollectionHolder
                  __typename
                }
                __typename
              }
            }

            fragment CollectionHolder on CollectionHolder {
              wallet
              numOwned
              numListed
              __typename
            }
            """
        }
    ]

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(base_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return response.json()[0]['data']['collectionHolderStats']['topHolders'][:15]
    else:
        return False


def get_profile_data(data: list | bool):
    result = []
    if data:
        for item in data:
            headers = {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9,ru;q=0.8,uz;q=0.7",
                "content-length": "167",
                "content-type": "application/json",
                "origin": "https://www.tensor.trade",
                "referer": "https://www.tensor.trade/",
                "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "solana-client": "js/1.0.0-maintenance",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            }
            data = {
                "method": "getBalance",
                "jsonrpc": "2.0",
                "params": [
                    item['wallet'],
                    {
                        "commitment": "confirmed"
                    }
                ],
                "id": f"{uuid.uuid4()}"
            }
            url = "https://tensor-tensor-ec08.mainnet.rpcpool.com/"
            response = requests.post(url, json=data, headers=headers)
            value = response.json()['result']['value']
            converted_value = value / 1e9
            formatted_value = "{:.4f}".format(converted_value)
            result.append(
                {
                    "wallet": item['wallet'],
                    "nft_hold": item['numOwned'],
                    "balance": formatted_value
                }
            )

    else:
        print("Response data error")
    return result


def add_to_file(data, filename):
    # with open(filename, "w") as file:
    #     # Write the header
    #     file.write(f"{'Wallet Address':<44} {'NFT Hold':<10} {'SOL Balance':<10}\n")
    #     file.write("=" * 64 + "\n")
    #
    #     # Write the data
    #     for entry in data:
    #         file.write(f"{entry['wallet']:<44} {entry['nft_hold']:<10} {entry['balance']:<10}\n")
    pdf = SimpleDocTemplate(filename, pagesize=landscape(letter))

    # Prepare table data
    table_data = [["Wallet Address", "NFT Hold", "SOL Balance"]]  # Header row
    for entry in data:
        table_data.append([entry["wallet"], entry["nft_hold"], entry["balance"]])

    # Create a Table
    table = Table(table_data)

    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)

    # Build the PDF
    elements = [table]
    pdf.build(elements)


def run_parse(telegram_id: int, nft_name: str):
    slug = get_slug(nft_name)
    data = get_graphql_api(slug)
    result = get_profile_data(data)
    sorted_data = sorted(result, key=lambda x: float(x["balance"]), reverse=True)
    add_to_file(sorted_data, f"{telegram_id}.pdf")

