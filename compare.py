import datetime
import email
import os
import re
import smtplib
import subprocess
import sys

CALIBRE_LIBRARY = os.environ["CALIBRE_LIBRARY"]
EMAIL = os.environ["EMAIL"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
SMTP = os.environ["SMTP"]


def main():
    filepaths = []
    for dirpath, dirnames, filenames in sorted(os.walk(CALIBRE_LIBRARY)):
        for filename in filenames:
            if dirpath.startswith(os.path.join(CALIBRE_LIBRARY, ".caltrash")):
                continue

            if filename.endswith(".original_epub"):
                filename = filename.replace(".original_epub", ".epub")
                filepath = os.path.join(dirpath, filename)
                filepaths.append(filepath)

    updates = {}
    start_time = datetime.datetime.now()
    for i, file in enumerate(filepaths):
        display_progress_bar(start_time, i, len(filepaths))
        ebook_meta_output = subprocess.getoutput(f'ebook-meta "{file}"')
        ebook_metadata = parse_metadata(ebook_meta_output)
        fetch_ebook_metadata_output = subprocess.getoutput(
            f"fetch-ebook-metadata -I {ebook_metadata['goodreads_id']}"
        )
        fetched_ebook_metadata = parse_metadata(fetch_ebook_metadata_output)
        update = compare_metadata(ebook_metadata, fetched_ebook_metadata)
        tries = 0
        while len(update) > 0 and tries < 3:
            tries += 1
            fetch_ebook_metadata_output = subprocess.getoutput(
                f"fetch-ebook-metadata -I {ebook_metadata['goodreads_id']}"
            )
            fetched_ebook_metadata = parse_metadata(
                fetch_ebook_metadata_output
            )
            update = compare_metadata(ebook_metadata, fetched_ebook_metadata)

        if len(update) > 0:
            updates[ebook_metadata["goodreads_id"]] = update

    display_progress_bar(start_time, len(filepaths), len(filepaths))
    print()

    if len(updates) > 0:
        send_email(updates)

    for book, update in updates.items():
        print(f"{book}: {update}")


def display_progress_bar(start_time, progress, end):
    elapsed_time = datetime.datetime.now() - start_time
    if progress == 0:
        sys.stdout.write(
            f"\r0% |{'.' * 50}| {progress}/{end} files ETA:  --:--:--"
        )
    elif progress == end:
        elapsed_time = str(elapsed_time).split(".", maxsplit=1)[0]
        sys.stdout.write(
            f"\r100% |{'=' * 49}>| {progress}/{end} files Time: {elapsed_time}"
        )
    else:
        percent = round(100 * progress / end)
        eta = (elapsed_time / progress) * (end - progress)
        eta = max(eta, datetime.timedelta(seconds=1))
        eta = str(eta).split(".", maxsplit=1)[0]
        sys.stdout.write(
            f"\r{percent}% "
            f"|{'=' * (percent//2 - 1)}>{'.' * (50 - percent//2)}| "
            f"{progress}/{end} files ETA:  {eta}"
        )

    sys.stdout.flush()


def parse_metadata(output):
    metadata = {}
    for line in output.split("\n"):
        if re.match(r"^Title\s*:", line):
            metadata["title"] = line.split(":")[1].strip()

        if re.match(r"^Author\(s\)\s*:", line):
            author = line.split(":")[1].split("[")[0].strip()
            metadata["authors"] = author.split(" & ")

        if re.match(r"^Series\s*:", line):
            metadata["series"] = line.split(":")[1].strip()

        if re.match(r"^Identifiers\s*:", line):
            identifiers = line.split()[2:]
            for identifier in identifiers:
                if identifier.startswith("goodreads"):
                    metadata["goodreads_id"] = identifier.strip(",")

    return metadata


def compare_metadata(m1, m2):
    update = []
    if m1.get("title") != m2.get("title"):
        update.append(f"Title: {m1.get('title')} -> {m2.get('title')}")

    if m1.get("authors") != m2.get("authors"):
        update.append(f"Author(s): {m1.get('authors')} -> {m2.get('authors')}")

    if m1.get("series") != m2.get("series"):
        update.append(f"Series: {m1.get('series')} -> {m2.get('series')}")

    return update


def send_email(updates):
    msg_content = "The following books have metadata updates:\n\n"
    for book, update in updates.items():
        goodreads_id = book.split(":")[1]
        msg_content += f"https://www.goodreads.com/book/show/{goodreads_id}\n"
        for u in update:
            msg_content += f"{u}\n"

        msg_content += "\n"

    msg = email.message.EmailMessage()
    msg["Subject"] = (
        "Metadata for some of your books have been updated on Goodreads"
    )
    msg["To"] = EMAIL
    msg["From"] = EMAIL
    msg.set_content(msg_content)
    smtp = smtplib.SMTP(SMTP)
    smtp.starttls()
    smtp.login(EMAIL, EMAIL_PASSWORD)
    smtp.send_message(msg)
    smtp.quit()


if __name__ == "__main__":
    main()
