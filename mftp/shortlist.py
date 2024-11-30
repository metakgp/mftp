import re
import io
import PyPDF2
import logging
from env import ROLL_NAME
from collections import defaultdict


def search(notices):
    notice_wise_shortlists = search_notice_wise_shortlists(notices)
    if notice_wise_shortlists:
        student_wise_shortlists = calc_student_wise_shortlists(notice_wise_shortlists)
        return student_wise_shortlists
    else:
        print("[NO NEW SHORTLISTS]", flush=True)
        return defaultdict(list)


def calc_student_wise_shortlists(notice_wise_shortlists):
    print("[PARSING STUDENT WISE SHORTLISTS]", flush=True)

    student_wise_shortlists = defaultdict(list)

    for notice_shortlist in notice_wise_shortlists:
        for roll, shortlists in notice_shortlist.items():
            student = student_wise_shortlists[roll]
            student.append(shortlists)

    for roll, shortlists in student_wise_shortlists.items():
        shortlists_str = " | ".join([
            f"{shortlist['company']} (#{shortlist['id']}) [{shortlist['count']}]"
            for shortlist in shortlists
        ])
        name = ROLL_NAME.get(roll)
        logging.info(f" [{name} ({roll})]: {shortlists_str}")

    return student_wise_shortlists


def search_notice_wise_shortlists(notices):
    print("[SEARCHING NOTICE WISE SHORTLISTS]", flush=True)

    notice_wise_shortlists = []
    for notice in notices:
        # Handling Shortists in Body
        try:
            body_shortlists = search_body(notice)
            if body_shortlists:
                notice_wise_shortlists.append(body_shortlists)
        except Exception as e:
            logging.error(f" Failed to parse shortlists from notice body ~ {str(e)}")
            continue

        # Handling Shortlist in attachment
        try:
            if "Attachment" in notice:
                attachment_shortlists = search_attachment(notice)
                if attachment_shortlists:
                    notice_wise_shortlists.append(attachment_shortlists)
        except Exception as e:
            logging.error(f" Failed to parse shortlists from attachment ~ {str(e)}")
            continue

    return notice_wise_shortlists


def search_body(notice):
    shortlists = defaultdict(dict)
    body_data = notice["BodyData"]
    body = body_data.decode_contents(formatter="html")

    for roll in ROLL_NAME.keys():
        count = body.count(roll)
        if count > 0:
            id_ = notice["UID"].split("_")[0]
            company = notice["Company"]
            name = ROLL_NAME.get(roll)

            shortlists[roll] = {
                "id": id_,
                "company": company,
                "count": count,
            }
            logging.info(
                f" [NOTICEBODY] {name} ({roll}) [{count}] -> {company} (#{id_})"
            )

    return shortlists


def search_attachment(notice):
    shortlists = defaultdict(dict)
    attachment = notice["Attachment"]

    for roll in ROLL_NAME.keys():
        count = parse_pdf_bytes(attachment, roll)
        if count > 0:
            id_ = notice["UID"].split("_")[0]
            company = notice["Company"]
            name = ROLL_NAME.get(roll)

            shortlists[roll] = {
                "id": id_,
                "company": company,
                "count": count,
            }
            logging.info(
                f" [ATTACHMENT] {name} ({roll}) [{count}] -> {company} (#{id_})"
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
