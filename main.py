import asyncio
from crawl4ai import AsyncWebCrawler
from scraper import extract_text
import os
from tqdm import tqdm

CLOUD_PLATFORM_SOURCES = {"AWS IoT": "https://aws.amazon.com/iot/",        # IoT cloud platforms
           "Azure IoT": "https://azure.microsoft.com/en-us",
           "Google Cloud IoT": "https://cloud.google.com/",
           "IBM Cloud": "https://www.ibm.com/solutions/cloud",
           "Oracle Cloud": "https://www.oracle.com/cloud/",
           "Alibaba Cloud": "https://www.alibabacloud.com/en?_p_lc=1",
           "Linode (Akamai Connected Cloud)": "https://www.linode.com/",
           "Tencent Cloud": "https://www.tencentcloud.com/",
           "Cloudflare": "https://www.cloudflare.com/",
           "Salesforce": "https://www.salesforce.com/"}

PRIVACY_POLICY_SOURCES = {"Google Privacy Policy": "https://policies.google.com/?hl=en",
           "Microsoft Privacy Policy": "https://www.microsoft.com/en-us/privacy",
           "SmartThings Privacy Policy": "https://eula.samsungiotcloud.com/legal/us/en/pps.html",
           "Amazon Alexa and Echo Privacy Policy": "https://www.amazon.com/gp/help/customer/display.html?nodeId=GVP69FUJ48X9DK8V",}


if __name__ == "__main__":

    for source_name in tqdm(CLOUD_PLATFORM_SOURCES):
        url = CLOUD_PLATFORM_SOURCES[source_name]
        asyncio.run(extract_text(source_name, url))