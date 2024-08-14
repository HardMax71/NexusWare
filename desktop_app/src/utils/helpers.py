import locale
from datetime import datetime
import barcode
from barcode.writer import ImageWriter

def format_currency(amount, currency='USD'):
    """Format a number as currency."""
    locale.setlocale(locale.LC_ALL, '')  # Use the user's default locale
    return locale.currency(amount, grouping=True, symbol=currency)

def parse_date(date_string, format='%Y-%m-%d'):
    """Parse a date string into a datetime object."""
    return datetime.strptime(date_string, format)

def generate_barcode(data, barcode_type='code128', output_file=None):
    """Generate a barcode image."""
    barcode_class = barcode.get_barcode_class(barcode_type)
    instance = barcode_class(data, writer=ImageWriter())
    if output_file:
        instance.save(output_file)
    else:
        return instance.render()
