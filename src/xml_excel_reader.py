import datetime
import io
import re
import zipfile

from lxml import etree as etree

import pandas as pd


class XMLExcelReader:
    # https://blog.adimian.com/2018/09/04/fast-xlsx-parsing-with-python/
    transform = etree.XSLT(etree.XML("""
    <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:sp="http://schemas.openxmlformats.org/spreadsheetml/2006/main" >
        <xsl:output method="text"/>
        <xsl:template match="/sp:worksheet/sp:sheetData/sp:row/sp:c">
            <xsl:value-of select="../@r"/> <xsl:text>,</xsl:text> <!-- GET ROW -->
            <xsl:value-of select="@r"/> <xsl:text>,</xsl:text> <!-- GET CELL REFERENCE -->
            <xsl:value-of select="@t"/> <xsl:text>,</xsl:text> <!-- GET CELL  TYPE -->
            <xsl:value-of select="translate(sp:v, '&#10;', '')"/> <xsl:text>\r\n</xsl:text> <!-- VALUE -->
        </xsl:template>
        <xsl:template match="text()"/> <!-- IGNORE (https://stackoverflow.com/a/45100263) -->
    </xsl:stylesheet>"""))

    namespaces = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    string_extractor = etree.XPath("/ns:sst/ns:si", namespaces=namespaces)
    stringify = etree.XPath("string()", smart_strings=False)

    get_worksheets = etree.XPath("//ns:sheet", namespaces=namespaces)

    sheet_dims = etree.XPath("/ns:worksheet/ns:dimension/@ref", namespaces=namespaces, smart_strings=False)

    numbers = re.compile(r'[0-9]+')

    def __init__(self, file_path_or_buffer):
        self.fh = zipfile.ZipFile(file_path_or_buffer)
        self.shared = self.load_shared()
        self.workbook = self.load_workbook()

    @property
    def sheet_names(self):
        return list(self.workbook.keys())

    def load_workbook(self):
        """Load workbook's sheet index"""
        r = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
        name = 'xl/workbook.xml'
        root = etree.parse(self.fh.open(name))
        res = {el.attrib['name']: el.attrib[f"{r}id"].lstrip("rId") for el in self.get_worksheets(root)}
        return res

    def load_shared(self):
        """Load shared strings"""
        name = 'xl/sharedStrings.xml'
        root = etree.parse(self.fh.open(name))

        # res = etree.XPath("/ns:sst/ns:si/string()", namespaces=self.namespaces, smart_strings=False)(root)  # Works in XPath 2.0

        return {str(pos): self.stringify(el) for pos, el in enumerate(self.string_extractor(root))}

    def _parse_sheet(self, root):
        """Parse XML tree to stacked CSV"""
        result = self.transform(root)
        return pd.read_csv(io.StringIO(str(result)), header=None, dtype="str", names=['row', 'cell', 'type', 'value'])

    def read(self, sheet_name, row_start: int = None, col_range: tuple = None):
        """Read sheet name to pandas dataframe"""
        min_col = col_range[0] if col_range is not None else None
        max_col = col_range[1] + 1 if col_range is not None else None
        row_start = row_start or None

        try:
            sheet_id = self.workbook[sheet_name]
        except KeyError:
            raise KeyError(f"Sheet {sheet_name} not in workbook. Valid sheets are: [{', '.join(self.workbook.keys())}]") from None
        sheet_path = f'xl/worksheets/sheet{sheet_id}.xml'
        root = etree.parse(self.fh.open(sheet_path))
        used_range = self.sheet_dims(root)[0]
        df = self._parse_sheet(root)
        del root

        # Ensure rows are numeric
        df['row'] = df['row'].fillna(0).astype("int64")

        # Add column numbers
        cols = df["cell"].str.replace(self.numbers, '')
        colmax = self._name_to_num(re.sub(self.numbers, "", used_range[1 + used_range.find(":"):]))
        keymap = {self._num_to_name(n): n for n in range(1, colmax + 1)}
        df['col'] = cols.map(keymap)
        del cols, keymap

        # Translate string contents
        cond = (df["type"] == 's') & (~df["value"].isna())  # Types: s=string, str=string literal, e=error, b=bool, NaN=number
        df.loc[cond, 'value'] = df.loc[cond, 'value'].map(self.shared)

        if all(df["col"].isna()):
            raise ValueError("Column not transformed properly")

        # Pivot everything
        df = df.pivot(index='row', columns='col', values='value').reset_index(drop=True)
        df = df.reindex(columns=range(1, max(df.columns) + 1))  # Fill out dataframe with columns (Excel used 1-based indexing)
        df.columns = range(df.shape[1])  # Convert the columns to 0-based indexing

        return df.iloc[row_start:, min_col:max_col].reset_index(drop=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fh.close()

    @staticmethod
    def _num_to_name(n):
        """Number to Excel-style column name,

        e.g., 1 = A, 26 = Z, 42 = AP, 18278 = ZZZ. (Limit of Excel is 16384=XFD)
        """
        name = ""
        while n > 0:
            n, r = divmod(n - 1, 26)
            name = chr(r + ord('A')) + name
        return name

    @staticmethod
    def _name_to_num(name):
        """Excel-style column name to number, e.g., A = 1, Z = 26, AA = 27, AAA = 703."""
        return int("".join([str(1 + ord(c) - ord('A')) for c in name.upper()]), base=26)


def datetime_from_excel(ordinal: float) -> datetime.datetime:
    epoch = datetime.datetime(1900, 1, 1)
    return epoch + datetime.timedelta(ordinal - 2)
