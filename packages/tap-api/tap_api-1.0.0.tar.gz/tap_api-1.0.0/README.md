# Proofpoint Targeted Attack Protection API Package

Library implements all of the functions of the TAP API via Python, except SIEM API currently. 

### Requirements:

* Python 3.9+
* requests
* pysocks

### Installing the Package

You can install the tool using the following command directly from Github.

```
pip install git+https://github.com/pfptcommunity/tap-api-python.git
```

or can install the tool using pip.

```
# When testing on Ubuntu 24.04 the following will not work:
pip install tap-api
```

If you see an error similar to the following:

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.

    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.

    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
```

You should use install pipx or you can configure your own virtual environment and use the command referenced above.

```
pipx install tap-api
```


### Creating an API client object
```python
from tap_api.v2 import *

if __name__ == '__main__':
    client = Client("<principal>", "<secret>")
```

### Querying the Campaign API
The Campaign API allows administrators to pull campaign IDs in a timeframe and specific details about campaigns, including:

- their description;
- the actor, malware family, and techniques associated with the campaign; and
- the threat variants which have been associated with the campaign

#### Getting campaign id metadata

Used to fetch a list of IDs of campaigns active in a time window sorted by the last updated timestamp.

```python
from datetime import timedelta, datetime, timezone
from tap_api.common import StartOffsetInterval, StartEndInterval, OffsetEndInterval, TimeWindow
from tap_api.v2 import Client

if __name__ == '__main__':
    client = Client("<principal>", "<secret>")
    campaign_data = client.campaign.ids(StartEndInterval(datetime.now(timezone.utc) - timedelta(hours=1), datetime.now(timezone.utc)))
    print(campaign_data.get_status())
    print(campaign_data.get_reason())
    for info in campaign_data.campaigns:
        print("\nCampaigns:")
        print(f"  ID: {info.id}")
        print(f"  Last Updated At: {info.last_updated_at}")
```
#### Getting campaign details

The sample below shows how to query detailed information for a given campaign.

```python
from tap_api.v2 import Client

if __name__ == '__main__':
    client = Client("<principal>", "<secret>")
    
    print(client.campaign["<campaign_id_here>"].uri)
    
    campaign_summary = client.campaign["<campaign_id_here>"]()

    print("HTTP Status:", campaign_summary.get_status())
    print("HTTP Reason:", campaign_summary.get_reason())
    print("\nCampaign:")
    print(f"  ID: {campaign_summary.id}")
    print(f"  Name: {campaign_summary.name}")
    print(f"  Description: {campaign_summary.description}")
    print(f"  Start Date: {campaign_summary.start_date}")
    for campaign_member in campaign_summary.campaign_members:
        print("\n  Campaign Member:")
        print(f"    ID: {campaign_member.id}")
        print(f"    Name: {campaign_member.name}")
        print(f"    Type: {campaign_member.type}")
        print(f"    Sub Type: {campaign_member.sub_type}")
        print(f"    Threat Time: {campaign_member.threat_time}")

    for actor in campaign_summary.actors:
        print("\n  Campaign Actor:")
        print(f"    ID: {actor.id}")
        print(f"    Name: {actor.name}")

    for malware in campaign_summary.malware:
        print("\n  Malware:")
        print(f"    ID: {malware.id}")
        print(f"    Name: {malware.name}")

    for technique in campaign_summary.techniques:
        print("\n  Malware:")
        print(f"    ID: {technique.id}")
        print(f"    Name: {technique.name}")

    for family in campaign_summary.families:
        print("\n  Family:")
        print(f"    ID: {family.id}")
        print(f"    Name: {family.name}")
```

### Querying the Forensics API

The Forensics API allows administrators to pull detailed forensic evidences about individual threats or campaigns
observed in their environment. These evidences could be used as indicators of compromise to confirm infection on a host,
as supplementary data to enrich and correlate against other security intelligence sources, or to orchestrate updates to
security endpoints to prevent exposure and infection.

#### Getting data for forensics for threats

```python
from tap_api.v2 import Client

if __name__ == '__main__':
    client = Client("<principal>", "<secret>")
    print(client.siem.uri)
    print(client.forensics.uri)
    aggregate_data = client.forensics.threat("<threat_id_here>")
    print("HTTP Status:", aggregate_data.get_status())
    print("HTTP Reason:", aggregate_data.get_reason())
    for report in aggregate_data.reports:
        print("\nReport:")
        print(f"  Scope: {report.scope}")
        print(f"  ID: {report.id}")
        print(f"  Name: {report.name}")
        print(f"  Threat Status: {report.threat_status}")

        for forensic in report.forensics:
            print("\n  Forensic:")
            print(f"    Type: {forensic.type}")
            print(f"    Display: {forensic.display}")
            print(f"    Engine: {forensic.engine}")
            print(f"    Malicious: {forensic.malicious}")
            print(f"    Time: {forensic.time}")
            print(f"    Note: {forensic.note or 'N/A'}")

            # Dump the `what` object. Note helper properties exist, but you must know the object type or type. 
            print("    What {}:".format(type(forensic.what).__name__))
            print(json.dumps(forensic.what, indent=4))

            # Dump platforms if available
            if forensic.platforms:
                print("    Platforms:")
                for platform in forensic.platforms:
                    print(f"      Name: {platform.name}")
                    print(f"      OS: {platform.os}")
                    print(f"      Version: {platform.version}")
```

#### Getting data for forensics for campaigns

```python
from tap_api.v2 import Client

if __name__ == '__main__':
    client = Client("<principal>", "<secret>")
    aggregate_data = client.forensics.campaign("<campaign_id_here>")
    print("HTTP Status:", aggregate_data.get_status())
    print("HTTP Reason:", aggregate_data.get_reason())
    for report in aggregate_data.reports:
        print("\nReport:")
        print(f"  Scope: {report.scope}")
        print(f"  ID: {report.id}")
        print(f"  Name: {report.name}")
        print(f"  Threat Status: {report.threat_status}")

        for forensic in report.forensics:
            print("\n  Forensic:")
            print(f"    Type: {forensic.type}")
            print(f"    Display: {forensic.display}")
            print(f"    Engine: {forensic.engine}")
            print(f"    Malicious: {forensic.malicious}")
            print(f"    Time: {forensic.time}")
            print(f"    Note: {forensic.note or 'N/A'}")

            # Dump the `what` object. Note helper properties exist, but you must know the object type or type.
            print("    What {}:".format(type(forensic.what).__name__))
            print(json.dumps(forensic.what, indent=4))

            # Dump platforms if available
            if forensic.platforms:
                print("    Platforms:")
                for platform in forensic.platforms:
                    print(f"      Name: {platform.name}")
                    print(f"      OS: {platform.os}")
                    print(f"      Version: {platform.version}")
```

### Querying the Threats API

```python
from tap_api.v2 import Client

if __name__ == '__main__':
    client = Client("<principal>", "<secret>")

    # Returns a threat summary dictionary
    threat_summary = client.threat.summary["<threat_id_here>"]()

    # Dictionary object also has data associated with the HTTP response.
    print("HTTP Status:", threat_summary.get_status())
    print("HTTP Reason:", threat_summary.get_reason())

    print("\nThreat Info:")
    print(f"  ID: {threat_summary.id}")
    print(f"  Identified At: {threat_summary.identified_at}")
    print(f"  Name: {threat_summary.name}")
    print(f"  Type: {threat_summary.type}")
    print(f"  Category: {threat_summary.category}")
    print(f"  Status: {threat_summary.status}")
    print(f"  Detection Type: {threat_summary.detection_type}")
    print(f"  Severity: {threat_summary.severity}")
    print(f"  Attack Spread: {threat_summary.attack_spread}")
    print(f"  Notable: {threat_summary.notable}")
    print(f"  Verticals: {threat_summary.verticals}")
    print(f"  Geographies: {threat_summary.geographies}")

    print("\n  Actors:")
    for actor in threat_summary.actors:
        print(f"    ID: {actor.id}")
        print(f"    Name: {actor.name}")

    print("\n  Families:")
    for family in threat_summary.families:
        print(f"    ID: {family.id}")
        print(f"    Name: {family.name}")

    print("\n  Malware:")
    for malware in threat_summary.malware:
        print(f"    ID: {malware.id}")
        print(f"    Name: {malware.name}")

    print("\n  Techniques:")
    for technique in threat_summary.techniques:
        print(f"    ID: {technique.id}")
        print(f"    Name: {technique.name}")

    print("\n  Brands:")
    for brand in threat_summary.brands:
        print(f"    ID: {brand.id}")
        print(f"    Name: {brand.name}")
```

### Querying the People API

The People API allows administrators to identify which users in their organizations were most attacked or are the top
clickers during a specified period.

```python
from tap_api.v2 import Client

if __name__ == '__main__':
    client = Client("<principal>", "<secret>")
    vap_info = client.people.vap()

    print("HTTP Status:", vap_info.get_status())
    print("HTTP Reason:", vap_info.get_reason())
    print("Total VAPs:", vap_info.total_vap_users)
    print("Interval:", vap_info.interval)
    print("Average Attack Index:", vap_info.average_attack_index)
    print("VAP Attack Threshold:", vap_info.vap_attack_index_threshold)

    for user in vap_info.users:
        identity = user.identity
        threat_statistics = user.threat_statistics

        print("\nUser Details:")
        print("  Email(s):", identity.emails)
        print("  Name:", identity.name or "N/A")
        print("  Department:", identity.department or "N/A")
        print("  Location:", identity.location or "N/A")
        print("  Title:", identity.title or "N/A")
        print("  VIP:", identity.vip)

        print("Threat Statistics:")
        print("  Attack Index:", threat_statistics.attack_index)
        print("  Threat Families:")
        for family in threat_statistics.families:
            print(f"    - {family.name}: {family.score}")
```

### Querying the URL Decoder API

The URL Decoder API allows users to decode URLs which have been rewritten by TAP to their original, target URL.

```python
from tap_api.v2 import Client

if __name__ == '__main__':
    client = Client("<principal>", "<secret>")
    decoded_urls = client.url.decode([
        "https://urldefense.proofpoint.com/v2/url?u=http-3A__links.mkt3337.com_ctt-3Fkn-3D3-26ms-3DMzQ3OTg3MDQS1-26r-3DMzkxNzk3NDkwMDA0S0-26b-3D0-26j-3DMTMwMjA1ODYzNQS2-26mt-3D1-26rt-3D0&d=DwMFaQ&c=Vxt5e0Osvvt2gflwSlsJ5DmPGcPvTRKLJyp031rXjhg&r=MujLDFBJstxoxZI_GKbsW7wxGM7nnIK__qZvVy6j9Wc&m=QJGhloAyfD0UZ6n8r6y9dF-khNKqvRAIWDRU_K65xPI&s=ew-rOtBFjiX1Hgv71XQJ5BEgl9TPaoWRm_Xp9Nuo8bk&e=",
        "https://urldefense.proofpoint.com/v1/url?u=http://www.bouncycastle.org/&amp;k=oIvRg1%2BdGAgOoM1BIlLLqw%3D%3D%0A&amp;r=IKM5u8%2B%2F%2Fi8EBhWOS%2BqGbTqCC%2BrMqWI%2FVfEAEsQO%2F0Y%3D%0A&amp;m=Ww6iaHO73mDQpPQwOwfLfN8WMapqHyvtu8jM8SjqmVQ%3D%0A&amp;s=d3583cfa53dade97025bc6274c6c8951dc29fe0f38830cf8e5a447723b9f1c9a",
        "https://urldefense.com/v3/__https://google.com:443/search?q=a*test&gs=ps__;Kw!-612Flbf0JvQ3kNJkRi5Jg!Ue6tQudNKaShHg93trcdjqDP8se2ySE65jyCIe2K1D_uNjZ1Lnf6YLQERujngZv9UWf66ujQIQ$"
    ])

    # DictionaryCollection object also has data associated with the HTTP response.
    print("HTTP Status:", decoded_urls.get_status())
    print("HTTP Reason:", decoded_urls.get_reason())
    print("Response Data:", json.dumps(decoded_urls, indent=4))
    for url_info in decoded_urls.urls():
        print("\nDecoded URL Info:")
        print(f"  Encoded URL: {url_info.encoded_url}")
        print(f"  Decoded URL: {url_info.decoded_url}")
        print(f"  Message GUID: {url_info.message_guid}")
        print(f"  Cluster Name: {url_info.cluster_name}")
        print(f"  Recipient Email: {url_info.recipient_email}")
        print(f"  Success: {url_info.success}")
        print(f"  Error: {url_info.error or 'N/A'}")
```

### Proxy Support

Socks5 Proxy Example:

```python
from tap_api.v2 import Client

if __name__ == '__main__':
    client = Client("<principal>", "<secret>")
    credentials = "{}:{}@".format("proxyuser", "proxypass")
    client.session.proxies = {'https': "{}://{}{}:{}".format('socks5', credentials, '<your_proxy>', '8128')}
```

HTTP Proxy Example (Squid):

```python
from tap_api.v2 import Client

if __name__ == '__main__':
    client = Client("<principal>", "<secret>")
    credentials = "{}:{}@".format("proxyuser", "proxypass")
    client.session.proxies = {'https': "{}://{}{}:{}".format('http', credentials, '<your_proxy>', '3128')}

```

### HTTP Timeout Settings

```python
from tap_api.v2 import Client

if __name__ == '__main__':
    client = Client("<principal>", "<secret>")
    # Timeout in seconds, connect timeout
    client.timeout = 600
    # Timeout advanced, connect / read timeout
    client.timeout = (3.05, 27)
```

### Limitations

Currently the SIEM API has not yet been implemented. 

For more information please see: https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation

