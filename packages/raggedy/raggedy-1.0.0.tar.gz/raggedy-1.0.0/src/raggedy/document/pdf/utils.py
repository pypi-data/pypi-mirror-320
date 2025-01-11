from PySide6.QtCore import QSize
from PySide6.QtGui import QImage, QColor, QPainter
from PySide6.QtPdf import QPdfDocument
from raggedy.document.subclasses.visual import VisualDocument
from os.path import basename

def fill_transparent(image: QImage, color: QColor = QColor(255, 255, 255)) -> QImage:
	"""
	Fills in the transparent pixels in 'image' with the specified 'color'.

	Args:
		image: the input QImage with potentially transparent pixels to fill in.
		color: the QColor to fill any transparent pixels with (default is white).

	Returns:
		QImage: a new QImage with the transparent pixels filled in.
	"""
	width, height = image.width(), image.height()
	background = QImage(width, height, QImage.Format.Format_ARGB32)
	background.fill(color)

	painter = QPainter(background)
	painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
	painter.drawImage(0, 0, image.convertToFormat(QImage.Format.Format_ARGB32))
	assert painter.end()

	return background

def pdf_page_to_image(
	filepath: str,
	doc: QPdfDocument,
	page: int,
	dpi: int = 300
) -> VisualDocument:
	"""
	Renders a page from a PDF document into a VisualDocument.
	Automatically fills any transparent pixels with solid white.
	It is the caller's responsibility to close the QPdfDocument when needed.

	Args:
		filepath: the original path to the PDF to parse filename from.
		doc: the already-loaded QPdfDocument containing the page.
		page: the page number to render (0-indexed).
		dpi: the dots per inch ("resolution") to render at (default is 300).

	Returns:
		VisualDocument: the PDF page rendered as an image.
	"""
	assert doc.status() == QPdfDocument.Status.Ready # PDF must be loaded

	size = doc.pagePointSize(page)
	width = int(size.width() * dpi / 72.0) # one point is 1/72 of an inch
	height = int(size.height() * dpi / 72.0)

	return VisualDocument(
		basename(filepath),
		fill_transparent(doc.render(page, QSize(width, height))),
	)
