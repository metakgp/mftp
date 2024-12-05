import os
import json
import logging
from env import ROLL_NUMBER
from datetime import datetime
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as bs
from endpoints import TPSTUDENT_URL, COMPANIES_URL


COMPANIES_FILE = f"{os.path.dirname(__file__)}/companies.json"


def filter(companies, filter):
    print('[FILTERING COMPANY UPDATES]', flush=True)

    filter_func = currently_open
    if filter.upper() == "OPEN":
        filter_func = currently_open
    elif filter.upper() == "OPEN_N":
        filter_func = open_not_applied # important
    elif filter.upper() == "APPLIED":
        filter_func = applied
    elif filter.upper() == "APPLIED_Y":
        filter_func = applied_available # important
    elif filter.upper() == "APPLIED_N":
        filter_func = applied_not_available # important

    filtered = []
    for company in companies:
        if filter_func(company):
            filtered.append(company)
            logging.info(
                f" {company['Name']} | {company['Role']} | {company['CTC']} | {company['End_Date']} | {company['Interview_Date']}"
            )

    return filtered


def fetch(session, headers, ssoToken):
    print('[FETCHING COMPANY UPDATES]', flush=True)

    session.post(
        TPSTUDENT_URL,
        data=dict(ssoToken=ssoToken, menu_id=11, module_id=26),
        headers=headers,
    )
    r = session.get(COMPANIES_URL, headers=headers)

    soup = bs(r.text, features="xml")
    xml_string = soup.prettify()
    xml_encoded = xml_string.encode("utf-8")
    root = ET.fromstring(xml_encoded)

    fetched_companies = []
    for row in root.findall("row"):
        jd_args = row.find("cell[4]").text.split("'")[5].split('"')
        jnf_id, com_id, year = jd_args[1], jd_args[3], jd_args[5]

        # Links
        company_details = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/TPComView.jsp?yop={year}&com_id={com_id}&user_type=SU"
        company_additional_details = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/AdmFilePDF.htm?type=COM&year={year}&com_id={com_id}"
        ppt = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/AdmFilePDF.htm?type=PPT&year={year}&com_id={com_id}"
        jd = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/TPJNFView.jsp?jnf_id={jnf_id}&com_id={com_id}&yop={year}&user_type=SU&rollno={ROLL_NUMBER}"
        apply_link_cv = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/TPJNFViewAction.jsp?jnf_id={jnf_id}&com_id={com_id}&year={year}&rollno={ROLL_NUMBER}&mode=ApplyCV"
        additional_jd = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/JnfMoreDet.jsp?mode=jnfMoreDet&rollno={ROLL_NUMBER}&year={year}&com_id={com_id}&jnf_id={jnf_id}"
        form_additional_details = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/AdmFilePDF.htm?type=JNF&year={year}&jnf_id={jnf_id}&com_id={com_id}"

        company_info = {
            "Name": row.find("cell[1]").text.split(">")[1].split("<")[0].strip(),
            "Company_Details": company_details,
            "Company_Additional_Details": company_additional_details,
            "PPT": ppt,
            "Role": row.find("cell[4]").text.split("'")[1].strip(),
            "Job_Description": jd,
            "Apply_Link_CV": apply_link_cv,
            "Additional_Job_Description": additional_jd,
            "CTC": get_ctc_with_currency(session, headers, additional_jd),
            "Form_Additional_Details": form_additional_details,
            "Application_Status": row.find("cell[9]").text.strip() if row.find("cell[9]").text.strip() else "N",
            "Start_Date": row.find("cell[10]").text.strip(),
            "End_Date": row.find("cell[11]").text.strip(),
            "Interview_Date": row.find("cell[12]").text.strip() if row.find("cell[12]").text.strip() else None,
        }
        
        fetched_companies.append(company_info)
    
    stored_companies = get_list()
    new_companies, modified_companies = get_new_and_modified_companies(fetched_companies, stored_companies)

    store_list(fetched_companies)

    return fetched_companies, new_companies, modified_companies


def get_new_and_modified_companies(fetched, stored, unique_key="Job_Description"):
    # Create dictionaries for quick lookup by the unique key
    stored_dict = {entry[unique_key]: entry for entry in stored}
    fetched_dict = {entry[unique_key]: entry for entry in fetched}

    new_entries = []
    updated_entries = []

    for key, fetched_entry in fetched_dict.items():
        if key not in stored_dict:
            # New entry
            new_entries.append(fetched_entry)
            logging.info(
                f" [NEW COMPANY]: {fetched_entry['Name']} | {fetched_entry['Role']} | {fetched_entry['CTC']} | {fetched_entry['End_Date']} | {fetched_entry['Interview_Date']}"
            )
        else:
            # Compare the values of the fetched entry with the stored entry
            stored_entry = stored_dict[key]
            if any(fetched_entry[k] != stored_entry.get(k) for k in fetched_entry):
                updated_entries.append(fetched_entry)
                logging.info(
                    f" [MODIFIED COMPANY]: {fetched_entry['Name']} | {fetched_entry['Role']} | {fetched_entry['CTC']} | {fetched_entry['End_Date']} | {fetched_entry['Interview_Date']}"
                )

    return new_entries, updated_entries


def store_list(companies):
    with open(COMPANIES_FILE, "w") as json_file:
        json.dump(companies, json_file, indent=2)


def get_list():
    try:
        with open(COMPANIES_FILE, "r") as json_file:
            return json.load(json_file)
    except json.JSONDecodeError as _:
        store_list([])
        return []
    except FileNotFoundError:
        store_list([])
        return []


# Downloads pdf content in bytes format
## Not used currently
def parse_link(session, link):
    stream = session.get(link, stream=True)
    attachment = b''
    for chunk in stream.iter_content(4096):
        attachment += chunk
    
    return attachment


def get_ctc_with_currency(session, headers, jd_url):
    jd_response = session.get(jd_url, headers=headers)
    html_content = jd_response.text.strip()
    soup = bs(html_content, "html.parser")

    row = soup.find_all("tr")[-1]
    column = row.find_all("td")[-1]
    ctc = column.text

    return ctc


def open_not_applied(company):
    return currently_open(company) and not applied(company)


def applied_not_available(company):
    return applied(company) and compare_deadline_gt(company, "Interview_Date")


def applied_available(company):
    return applied(company) and compare_deadline_lt(company, "Interview_Date")


def applied(company):
    return company["Application_Status"] == "Y"


def currently_open(company):
    return compare_deadline_lt(company, "End_Date")


def compare_deadline_gt(company, deadline_key):
    current_time = datetime.now()
    deadline = parse_date(company, deadline_key)

    return deadline is None or current_time > deadline


def compare_deadline_lt(company, deadline_key):
    current_time = datetime.now()
    deadline = parse_date(company, deadline_key)

    return deadline is None or current_time < deadline


def parse_date(company, date_key):
    date_format = "%d-%m-%Y %H:%M"
    
    date = None
    if company.get(date_key):
        try:
            date = datetime.strptime(company[date_key], date_format)
        except ValueError as e:
            logging.error(f" Failed to parse date for {company['Name']} ~ {str(e)}")
            date = None

    return date

