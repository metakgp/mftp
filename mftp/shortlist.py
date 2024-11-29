import re
import io
import PyPDF2
import logging
from collections import defaultdict
from env import HOSTER_INTERESTED_ROLLS, ROLL_MAIL, ROLL_NAME


def from_notice_body(notice):
    shortlists = defaultdict(dict)
    body_data = notice["BodyData"]
    body = body_data.decode_contents(formatter="html")

    for roll in HOSTER_INTERESTED_ROLLS:
        count = body.count(roll)
        if count > 0:
            id_ = notice["UID"].split("_")[0]
            company = notice["Company"]
            name = ROLL_NAME.get(roll)
            mails = ROLL_MAIL.get(roll)

            shortlists[roll] = {
                "id": id_,
                "company": company,
                "name": name,
                "count": count,
                "mails": mails,
            }
            logging.info(
                f" [SHORTLIST (noticebody)] {name} ({count}) -> {company} (#{id_})"
            )

    return shortlists


def from_attachment(notice):
    shortlists = defaultdict(dict)
    attachment = notice["Attachment"]

    for roll in HOSTER_INTERESTED_ROLLS:
        count = search_pdf_bytes(attachment, roll)
        if count > 0:
            id_ = notice["UID"].split("_")[0]
            company = notice["Company"]
            name = ROLL_NAME.get(roll)
            mails = ROLL_MAIL.get(roll)

            shortlists[roll] = {
                "id": id_,
                "company": company,
                "name": name,
                "count": count,
                "mails": mails,
            }
            logging.info(
                f" [SHORTLIST (attachment)] {name} ({count}) -> {company} (#{id_})"
            )

    return shortlists


def search_pdf_bytes(pdf_bytes, search_string):
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        count = 0
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            # Normalize text: remove spaces between alphanumeric characters
            normalized_text = re.sub(r"(?<=\w) (?=\w)", "", page_text)
            count += normalized_text.count(search_string)

        return count

    except Exception as e:
        logging.error(f" Error searching PDF for {search_string}: {e}")
        return 0
