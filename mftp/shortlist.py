import re
import io
import PyPDF2
import logging
from collections import defaultdict
from env import HOSTER_INTERESTED_ROLLS, ROLL_MAIL, ROLL_NAME


def search(notices):
    print('[SEARCHING SHORTLISTS]', flush=True)

    shortlists = []
    for notice in notices:
        # Handling Shortists in Body
        try:
            body_shortlists = search_body(notice)
            if body_shortlists:
                shortlists.append(body_shortlists)
        except Exception as e:
            logging.error(f" Failed to parse shortlists from notice body ~ {str(e)}")
            continue

        # Handling Shortlist in attachment
        try:
            if 'Attachment' in notice:
                attachment_shortlists = search_attachment(notice)
                if attachment_shortlists:
                    shortlists.append(attachment_shortlists)
        except Exception as e:
            logging.error(f" Failed to parse shortlists from attachment ~ {str(e)}")
            continue

    return shortlists


def search_body(notice):
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
                f" [NOTICEBODY] {name} ({count}) -> {company} (#{id_})"
            )

    return shortlists


def search_attachment(notice):
    shortlists = defaultdict(dict)
    attachment = notice["Attachment"]

    for roll in HOSTER_INTERESTED_ROLLS:
        count = parse_pdf_bytes(attachment, roll)
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
                f" [ATTACHMENT] {name} ({count}) -> {company} (#{id_})"
            )

    return shortlists


def parse_pdf_bytes(pdf_bytes, search_string):
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
