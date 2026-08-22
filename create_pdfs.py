from pypdf import PdfWriter


def create_pdf(filename, text):
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)

    with open(filename, "wb") as file:
        writer.write(file)


create_pdf("first.pdf", "First PDF")
create_pdf("second.pdf", "Second PDF")

print("Two PDF files created successfully!")