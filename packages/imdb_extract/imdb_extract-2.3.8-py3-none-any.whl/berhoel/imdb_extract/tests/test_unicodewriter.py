"""Testing Unicode writer"""

import io

from berhoel.imdb_extract import unicodewriter

__date__ = "2024/08/03 21:48:15 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2013 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


def test_writerow_1():
    out = io.StringIO()
    writer = unicodewriter.UnicodeWriter(out)
    writer.writerow((1, 2, 3))

    assert out.getvalue().strip() == "1,2,3"


def test_writerow_2():
    out = io.StringIO()
    writer = unicodewriter.UnicodeWriter(out)
    writer.writerow(("ä", "ö", "ü"))

    data = out.getvalue().strip()
    assert data == "ä,ö,ü"
