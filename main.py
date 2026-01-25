import asyncio
from crawl4ai import AsyncWebCrawler
from scraper import extract_text, extract_text_from_pdf
import os
from tqdm import tqdm
import pandas as pd
from annotate_dataset import generate_triples

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
           "Amazon Alexa and Echo Privacy Policy": "https://www.amazon.com/gp/help/customer/display.html?nodeId=GVP69FUJ48X9DK8V",
           "Cisco Privacy Policy": "https://store.google.com/magazine/google_pixel_watch_compare?hl=en-US&pli=1",
           "Apple Privacy Policy": "https://www.apple.com/legal/privacy/en-ww/",
           "Huawei Privacy Policy": "https://consumer.huawei.com/en/privacy/privacy-statement-huawei/",
           "Samsung Privacy Policy": "https://www.samsung.com/us/account/privacy-policy/",
           "Ring Privacy Policy": "https://ring.com/privacy-notice?srsltid=AfmBOoo0ZH4T_iO5KXl9j1oenf05o819_C_nf95hTSg4BXXSmBgkJOyB",
           "Schneider Electric": "https://www.se.com/us/en/about-us/legal/data-privacy/"}

AMAZON_PRODUCT_PAGES = {"Apple Watch Series 11 Amazon Page": "https://www.amazon.com/Apple-Watch-Smartwatch-Aluminum-Always/dp/B0FQF9ZX7P/ref=sr_1_11?crid=108RRKEJVL294&dib=eyJ2IjoiMSJ9.zTbJrgpN_9X1fDio2GYFftYmRx9CG5wkuhzMr0eSZitrEWEZOnae9x0wLm1eZuzrMWn5RyzxvMs3whriDBMoWJRZ1FbDal-lDII--jicMIGVUkHjEE_HEs9UVZYGYgly3Y5m7v_H6Pr3ZWCJvytRI7mEYIlKUvTv4sxXPy9RLWeXqpX1tTn52Rd4S-I83sSXe-_abhlskNn-GXfFpZgyGpdOqXm_OLpg-0NIBmNHUJM.8lwwfMVOo7q35Wtg1NTLKjWJ994mL1yWjMWE6gc61wU&dib_tag=se&keywords=smart%2Bwatch&qid=1769265919&sprefix=smar%2Caps%2C920&sr=8-11&th=1",
                        "Amazon Fire TV Stick Amazon Page": "https://www.amazon.com/Amazon-newest-AI-powered-Search-million/dp/B0F7Z4QZTT/ref=sr_1_1?crid=14M57D8W5UV3C&dib=eyJ2IjoiMSJ9.5Jq38u5xJ09qYPVqbhrMIoajvL40XxHiiqOqJOuWz_n27pfWiVT3NWQw9VDWhodQPk2hU3ibMfeOhLrvXOcp74yeWDSXhGQrn7gmAZgy8BjdU0O5slKOcnB9qe-dUZSG1NgKfR2g_ZoEW6-p4ntN-AmP3iDQAiFNFcbSyPtF0ILo2aPSbI4-kDnZR-4ilUvaL1uBD5suci1Gzfrc_X9CbURdZyqzXrlb2Y_gPvirFLA.b_5Fjh99Ml_1MSWh8NBsMBsRFjHvlzAnji0UB4JiPLA&dib_tag=se&keywords=amazon%2Bfire%2Btv&qid=1769266378&sprefix=amazon%2Bfi%2Caps%2C509&sr=8-1&th=1",
                        "Amazon Echo Dot Amazon Page": "http://amazon.com/Amazon-vibrant-helpful-routines-Charcoal/dp/B09B8V1LZ3/ref=sr_1_2?crid=MYQRPVLYJQZI&dib=eyJ2IjoiMSJ9.B7_8O8bxrKGFgKiTuA3oziI0IZTGCw5wmNUcr1eY0lPa_7bNsVhcfgv18ygxnktbzu_i6QJDa1EJfRpFx15KRPAEkhW86i9TjSF0BV7gWAX7eRN5Z7BCv7uf0O3uwZJG84k2KLZF-C92DoY7jwE1hg1lzZaxUKW9yRkxmoc0FKUAj5kEFtvIuVn4njI4r2nNVx44PzKELL75rhlK4B790_9ysmT0leb8v6wZvAps9D8.zXg0Q9gmYx7NYqmI6XqGPdBkpC5S7rexhxGD4M8Smqg&dib_tag=se&keywords=amazon+echo&qid=1769266437&sprefix=amazon+echo%2Caps%2C330&sr=8-2",
                        "Samsung Smart Fridge Amazon Page": "https://www.amazon.com/SAMSUNG-RF29DB9900QD-Stainless-4-Door-Refrigerator/dp/B0DDJPDNVP/ref=sr_1_3?crid=2B2UBLZ0GGSSA&dib=eyJ2IjoiMSJ9.edENUNDH9WToSqqbfE0pmAP6Z1EgUXAUmwAwcfgQl5n_Fkdpke7Mu6-nBhYtT9QmpCP32EBGeTXVn81FM039KBYBctjEbMFTAAzy5cvk-ABFDRbLZus8Qfdyb7ZCLrqQ7sAkZdicD2Rr63TWZQW0ChvCEpFRnNpQl5rbFJcAuRmvWpSTrHuJLff8raWcCkGsxt91P6LBErPh24tB_XbgovwCW9--_eYvJmqXUlTYLKI.x2FjVbkY0UkHM4WHudDudcoOCaUZhA5vofTutkpk6uY&dib_tag=se&keywords=smart+fridge&qid=1769266480&sprefix=smart+fridg%2Caps%2C265&sr=8-3",
                        "Govee Smart Light Bulbs Amazon Page": "https://www.amazon.com/Govee-Changing-Dynamic-Bluetooth-Assistant/dp/B09B7NQT2K/ref=sr_1_2?crid=3BYOT361Q1WPY&dib=eyJ2IjoiMSJ9.lVB7GzavqCrBfgQjF8OOHVIl-cm2Lo1IR50FXlbHMCFTQccOV0MZZ9mSVU4Q_DfUgJNFiS6XqTewCzsZS8CsDHu46HQ9t_J7HOWCUW7G0VSJ4Bluvpw-p4rOQ6hDqgwN0s_6puCT2l7hTLKkWTdZc1quBz8tbKxeixUfQKHyEJCxT0e7TlbBHm0gKgU_jZHHHkEBwat8pygPAE-R_Nd5KBycsOS4bXFndCyxLvBEz4plQSyMu9KsPe0ULzhLhjPqfhiGfN0-8AhqFHGVM4OStt_HsgBSSu5Yu-0eT448-6k.nssb7TbMTHvTjG_6vLYHQUdVdS7XpTDwedNjWesT78o&dib_tag=se&keywords=smart+lighting&qid=1769266544&sprefix=smart+lightin%2Caps%2C227&sr=8-2",
                        "Aeotec Smart Home Hub Amazon Page": "https://www.amazon.com/Aeotec-SmartThings-Gateway-Compatible-Assistant/dp/B08TWDNQ5Q/ref=sr_1_11?crid=DYIO1UN21WCJ&dib=eyJ2IjoiMSJ9.JL-1xoYpxP8p6YmGk8TF-b3Y5Mgk3kpoBQOeeLC6_rfyDORB_v3-wG2-KYTGgadv12HqQpxHEY5GTdCA0qJsB9QsRFvwsYP2SF2I51i1Heq81T2rDDvKQoHing6tjfPzCD94FkFyiEOTrxiaTcmHXzY_EDpQpfmAslc7e6xHo78jIB2YsuEcj0hXIr8tse-uSsQVw317pzklunYTFTqoBrs7ewxpOznzVlg1ZOBAVv6d6GIcbUp8YaT9mBjO-zypHj6gRZoUPQthL6mMMf-GJ-iZZZHvU3eMEJkpv168Eb8.zZeWbavz3VpgLN9jvyemRc6zpn6gMniMKZMsO8XDhcE&dib_tag=se&keywords=smart%2Bthings&qid=1769266580&sprefix=smart%2B%2Caps%2C459&sr=8-11&th=1",
                        "Samsung Galaxy Smart Tag Amazon Page": "http://amazon.com/SAMSUNG-SmartTag2-Bluetooth-Tracker-Tracking/dp/B0CCBXRYRC/ref=sr_1_16?crid=DYIO1UN21WCJ&dib=eyJ2IjoiMSJ9.JL-1xoYpxP8p6YmGk8TF-b3Y5Mgk3kpoBQOeeLC6_rfyDORB_v3-wG2-KYTGgadv12HqQpxHEY5GTdCA0qJsB9QsRFvwsYP2SF2I51i1Heq81T2rDDvKQoHing6tjfPzCD94FkFyiEOTrxiaTcmHXzY_EDpQpfmAslc7e6xHo78jIB2YsuEcj0hXIr8tse-uSsQVw317pzklunYTFTqoBrs7ewxpOznzVlg1ZOBAVv6d6GIcbUp8YaT9mBjO-zypHj6gRZoUPQthL6mMMf-GJ-iZZZHvU3eMEJkpv168Eb8.zZeWbavz3VpgLN9jvyemRc6zpn6gMniMKZMsO8XDhcE&dib_tag=se&keywords=smart+things&qid=1769266580&sprefix=smart+%2Caps%2C459&sr=8-16",
                        "GHome Smart Plug Amazon Page": "https://www.amazon.com/GHome-Smart-Compatible-Function-Required/dp/B0D7ZW512L/ref=sr_1_54?crid=DYIO1UN21WCJ&dib=eyJ2IjoiMSJ9.JL-1xoYpxP8p6YmGk8TF-b3Y5Mgk3kpoBQOeeLC6_rfyDORB_v3-wG2-KYTGgadv12HqQpxHEY5GTdCA0qJsB9QsRFvwsYP2SF2I51i1Heq81T2rDDvKQoHing6tjfPzCD94FkFyiEOTrxiaTcmHXzY_EDpQpfmAslc7e6xHo78jIB2YsuEcj0hXIr8tse-uSsQVw317pzklunYTFTqoBrs7ewxpOznzVlg1ZOBAVv6d6GIcbUp8YaT9mBjO-zypHj6gRZoUPQthL6mMMf-GJ-iZZZHvU3eMEJkpv168Eb8.zZeWbavz3VpgLN9jvyemRc6zpn6gMniMKZMsO8XDhcE&dib_tag=se&keywords=smart+things&qid=1769266580&sprefix=smart+%2Caps%2C459&sr=8-54",
                        "Ring Doorbell Camera Amazon Page": "https://www.amazon.com/GHome-Smart-Compatible-Function-Required/dp/B0D7ZW512L/ref=sr_1_54?crid=DYIO1UN21WCJ&dib=eyJ2IjoiMSJ9.JL-1xoYpxP8p6YmGk8TF-b3Y5Mgk3kpoBQOeeLC6_rfyDORB_v3-wG2-KYTGgadv12HqQpxHEY5GTdCA0qJsB9QsRFvwsYP2SF2I51i1Heq81T2rDDvKQoHing6tjfPzCD94FkFyiEOTrxiaTcmHXzY_EDpQpfmAslc7e6xHo78jIB2YsuEcj0hXIr8tse-uSsQVw317pzklunYTFTqoBrs7ewxpOznzVlg1ZOBAVv6d6GIcbUp8YaT9mBjO-zypHj6gRZoUPQthL6mMMf-GJ-iZZZHvU3eMEJkpv168Eb8.zZeWbavz3VpgLN9jvyemRc6zpn6gMniMKZMsO8XDhcE&dib_tag=se&keywords=smart+things&qid=1769266580&sprefix=smart+%2Caps%2C459&sr=8-54",
                        "Ring Indoor Camera Amazon Page": "https://www.amazon.com/introducing-the-all-new-Ring-Indoor-Cam/dp/B0B6GLQJMV/ref=sr_1_1?dib=eyJ2IjoiMSJ9._Gjw85RCyMzZxZF9-1GrsAeNAd8-4Pl0VlhFW2DbZ9QFgAGpUjtQALOjkzGvp8KqqLSOGN1Mv-lqK6c4CK_-O1jFCV-FEj6HWr-F03Uzq0-m9CAvcehxrPwYIGBnf-Tu9Y5qNmwDCf_CmOTeajNtqEB9OBaCAuyFwUwOpZuTHOeYJ-l2Nsd0ZvPf78ZuaJBjY6kqkIu3zky1jhBEP4kv2wDy7D7CizDIxIauaY2ZED8.jSF85GPr54yVCeU3pZ2xZzIzqpiiN28nAjnc2RKc9hg&dib_tag=se&keywords=ring%2Bcamera&qid=1769266741&sr=8-1&th=1"}

REVIEW_SOURCES = {"Ring Camera Review": "https://www.safehome.org/home-security-cameras/ring/reviews/",
                  "Google Smart Home Devices Review": "https://www.cnet.com/home/smart-home/best-google-smart-home-devices/",
                  "Google Smart Thermostat Review": "https://www.consumerreports.org/appliances/thermostats/google-nest-thermostat-review-a9480620820/",
                  "Fitbit Review": "https://www.wareable.com/features/what-fitbit-tracker-should-you-buy",
                  "Google vs Fitbit Review": "https://store.google.com/magazine/google_pixel_watch_compare?hl=en-US&pli=1",
                  "Govee Lights Review": "https://www.reddit.com/r/Govee/comments/1efe0nv/how_well_do_govee_permanent_outdoor_lights/",
                  "SmartThings Review": "https://www.pcworld.com/article/2480454/samsung-smartthings-station-review.html"}


SCHOLARLY_SOURCES_FOLDER = "scholarly_papers"
OUTPUT_CSV_FILE = "iot_web_dataset.csv"

EXTRACT_TEXT = False
MAKE_DATASET_CSV = False
GENERATE_TRIPLES = True



if __name__ == "__main__":

    if EXTRACT_TEXT:

        # for source_name in tqdm(CLOUD_PLATFORM_SOURCES):
        #     url = CLOUD_PLATFORM_SOURCES[source_name]
        #     asyncio.run(extract_text(source_name, url))

        # for source_name in tqdm(AMAZON_PRODUCT_PAGES):
        #     url = AMAZON_PRODUCT_PAGES[source_name]
        #     asyncio.run(extract_text(source_name, url))

        # for source_name in tqdm(REVIEW_SOURCES):
        #     url = REVIEW_SOURCES[source_name]
        #     asyncio.run(extract_text(source_name, url))

        # for source_name in tqdm(PRIVACY_POLICY_SOURCES):
        #     url = PRIVACY_POLICY_SOURCES[source_name]
        #     asyncio.run(extract_text(source_name, url))


        for file in os.listdir(SCHOLARLY_SOURCES_FOLDER):
                PDF = os.path.join(SCHOLARLY_SOURCES_FOLDER, file)
                print(f"Processing file: {PDF}")
                extract_text_from_pdf(PDF)

    if MAKE_DATASET_CSV:

        data_list = []
         
        # adds all the web sources
        for source in [CLOUD_PLATFORM_SOURCES, AMAZON_PRODUCT_PAGES, REVIEW_SOURCES, PRIVACY_POLICY_SOURCES]:
            for source_name in tqdm(source):
                text_file = f"raw text/{source_name.replace(' ', '_')}_raw_text.txt"
                data_dict = {"source name": source_name, "url": source[source_name], "text file": text_file}

                data_list.append(data_dict)
        
        # adds all the scholarly paper sources
        for file in tqdm(os.listdir(SCHOLARLY_SOURCES_FOLDER)):
                text_file = f"raw text/{file.replace('.pdf', '.txt').replace(' ', '_')}"
                data_dict = {"source name": file.replace('.pdf', '.txt'), "url": "", "text file": text_file}
                data_list.append(data_dict)

        # creates a DataFrame and saves it as a CSV file
        df = pd.DataFrame(data_list)
        
        df.to_csv(OUTPUT_CSV_FILE, index=False)

    if GENERATE_TRIPLES:
         generate_triples(OUTPUT_CSV_FILE)