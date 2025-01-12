import re
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from lxml.html import HtmlElement
from pydantic import HttpUrl

from licitpy.parsers.base import BaseParser
from licitpy.types.attachments import Attachment, FileType
from licitpy.types.geography import Region
from licitpy.types.tender.open_contract import OpenContract, PartyRoleEnum
from licitpy.types.tender.status import StatusFromImage, StatusFromOpenContract
from licitpy.types.tender.tender import Item, Tier, Unit


class TenderParser(BaseParser):

    def get_tender_opening_date_from_tender_ocds_data(
        self, data: OpenContract
    ) -> datetime:

        # The date comes as if it were UTC, but it is actually America/Santiago
        # - 2024-11-06T11:40:34Z -> 2024-11-06 11:40:34-03:00

        tender = data.records[0].compiledRelease.tender

        # "startDate": "2024-10-25T15:31:00Z",
        start_date = tender.tenderPeriod.startDate

        return datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=ZoneInfo("America/Santiago")
        )

    def get_closing_date_from_eligibility(self, html: str) -> datetime:
        # Extract the closing date for the eligibility phase (idoneidad técnica).
        # This date marks the final deadline for all participants to submit their initial technical eligibility documents.
        # After this point, only participants who meet the technical requirements can proceed.

        # Example date format from the HTML: "16-12-2024 12:00:00"
        closing_date = self.get_text_by_element_id(html, "lblFicha3CierreIdoneidad")

        # Parse the extracted date string into a datetime object, ensuring the correct format and time zone.
        return datetime.strptime(closing_date, "%d-%m-%Y %H:%M:%S").replace(
            tzinfo=ZoneInfo(
                "America/Santiago"
            )  # Set the time zone to Chile's local time.
        )

    def get_closing_date_from_html(self, html: str) -> datetime:
        # Check if the eligibility closing date (idoneidad técnica) exists in the HTML.
        # If lblFicha3CierreIdoneidad exists, it indicates that the process includes an eligibility phase.
        # In such cases, the usual closing date element (lblFicha3Cierre) contains a string like
        # "10 días a partir de la notificación 12:00" instead of a concrete date.
        if self.has_element_id(html, "lblFicha3CierreIdoneidad"):
            # Extract and return the eligibility closing date as the definitive closing date.
            # The eligibility phase defines the last moment when anyone can participate.
            return self.get_closing_date_from_eligibility(html)

        # If lblFicha3CierreIdoneidad does not exist, assume lblFicha3Cierre contains a concrete closing date.
        # Example: "11-11-2024 15:00:00"
        closing_date = self.get_text_by_element_id(html, "lblFicha3Cierre")

        # Parse the extracted date string into a datetime object, ensuring the correct format and time zone.
        return datetime.strptime(closing_date, "%d-%m-%Y %H:%M:%S").replace(
            tzinfo=ZoneInfo(
                "America/Santiago"
            )  # Set the time zone to Chile's local time.
        )

    def get_closing_date_from_tender_ocds_data(
        self, data: OpenContract
    ) -> datetime | None:
        """
        Get the closing date of a tender from its OCDS data.
        """

        tender = data.records[0].compiledRelease.tender

        # eg: "endDate": "2024-10-25T15:30:00Z",
        end_date = tender.tenderPeriod.endDate

        if end_date is None:
            return None

        return datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=ZoneInfo("America/Santiago")
        )

    def get_tender_status_from_tender_ocds_data(
        self, data: OpenContract
    ) -> StatusFromOpenContract:
        """
        Get the status of a tender from its OCDS data.
        """
        tender = data.records[0].compiledRelease.tender

        return tender.status

    def get_tender_title_from_tender_ocds_data(self, data: OpenContract) -> str:
        """
        Get the title of a tender from its OCDS data.
        """

        tender = data.records[0].compiledRelease.tender

        return tender.title

    def get_tender_description_from_tender_ocds_data(self, data: OpenContract) -> str:
        """
        Get the description of a tender from its OCDS data.
        """

        tender = data.records[0].compiledRelease.tender

        return tender.description

    def get_tender_region_from_tender_ocds_data(self, data: OpenContract) -> Region:
        """
        Retrieves the region of a tender from its OCDS data.
        """

        # Find the participants in the tender
        parties = data.records[0].compiledRelease.parties

        # Filter the participants who have the role of procuringEntity,
        # which represents the buying entity.
        procuring_entities = [
            party for party in parties if PartyRoleEnum.PROCURING_ENTITY in party.roles
        ]

        # If there is not exactly one entity with the role of procuringEntity, raise an error.
        if len(procuring_entities) != 1:
            raise ValueError(
                "There must be exactly one entity with the role of procuringEntity."
            )

        # Retrieve the address of the procuring entity.
        address = procuring_entities[0].address

        # If the address or region is missing, raise an error.
        if address is None or address.region is None:
            raise ValueError(
                "The address or region is missing for the procuring entity."
            )

        return address.region

    def get_tender_tier(self, code: str) -> Tier:
        """
        Get the budget tier of a tender based on its code.
        """

        return Tier(code.split("-")[-1:][0][:2])

    def get_tender_status_from_html(self, html: str) -> StatusFromImage:
        """
        Get the status of a tender based on its HTML content.
        """
        status = self.get_src_by_element_id(html, "imgEstado")

        return StatusFromImage(status.split("/")[-1].replace(".png", ""))

    def get_tender_code_from_tender_ocds_data(self, data: OpenContract) -> str:
        """
        Get the code of a tender from its OCDS data.
        """

        return str(data.uri).split("/")[-1].strip()

    def _get_table_attachments(self, html: str) -> HtmlElement:
        """
        Get the table containing the attachments from the HTML content.
        """

        table = self.get_html_element_by_id(html, "DWNL_grdId")

        if not table:
            raise ValueError("Table with ID 'DWNL_grdId' not found")

        return table[0]

    def _get_table_attachments_rows(self, table: HtmlElement) -> List[HtmlElement]:
        """
        Get the rows of the table containing the attachments.
        """

        rows = table.xpath("tr[@class]")

        if not rows:
            raise ValueError("No rows found in the table")

        return rows

    def _parse_size_attachment(self, td: HtmlElement) -> int:
        """
        Parse the size of an attachment from the HTML content.
        """

        size_text: str = td.xpath("span/text()")[0]
        match = re.match(r"(\d+)\s*Kb", size_text.strip())

        if not match:
            raise ValueError(f"Invalid size format: {size_text}")

        size_kb = int(match.group(1))

        return size_kb * 1024

    def _extract_attachment_id(self, td: HtmlElement) -> str:
        """
        Extract the attachment ID from the HTML content.
        """

        input_id = td.xpath("input/@id")

        if not input_id:
            raise ValueError("No input ID found in the first column")

        match = re.search(r"ctl(\d+)", input_id[0])

        if not match:
            raise ValueError("No match found for attachment ID")

        return match.group(1)

    def _extract_content_from_attachment_row(self, td: HtmlElement) -> str | None:
        """
        Extract the content from an attachment row in the HTML content.
        """

        content = td.xpath("span/text()")

        if content:
            return content[0]

        return None

    def get_attachments(self, html: str) -> List[Attachment]:
        """
        Get the attachments of a tender from the HTML content.
        """

        table = self._get_table_attachments(html)
        rows: List[HtmlElement] = self._get_table_attachments_rows(table)

        attachments: List[Attachment] = []

        for tr in rows:
            td: List[HtmlElement] = tr.xpath("td")

            attachment_id: str = self._extract_attachment_id(td[0])
            name = self._extract_content_from_attachment_row(td[1])
            attachment_type = self._extract_content_from_attachment_row(td[2])

            description = self._extract_content_from_attachment_row(td[3])

            size: int = self._parse_size_attachment(td[4])
            upload_date = self._extract_content_from_attachment_row(td[5])

            if not name:
                raise ValueError("Attachment name not found")

            # Bases_686617-1-L124.pdf
            file_type = FileType(name.split(".")[-1].lower().strip())

            attachment = Attachment(
                **{
                    "id": attachment_id,
                    "name": name,
                    "type": attachment_type,
                    "description": description,
                    "size": size,
                    "upload_date": upload_date,
                    "file_type": file_type,
                }
            )

            attachments.append(attachment)

        return attachments

    def get_attachment_url_from_html(self, html: str) -> HttpUrl:
        """
        Get the URL of an attachment from the HTML content.
        """

        attachment_url = self.get_on_click_by_element_id(html, "imgAdjuntos")

        url_match = re.search(r"ViewAttachment\.aspx\?enc=(.*)','", attachment_url)

        if not url_match:
            raise ValueError("Attachment URL hash not found")

        enc: str = url_match.group(1)
        url = f"https://www.mercadopublico.cl/Procurement/Modules/Attachment/ViewAttachment.aspx?enc={enc}"

        return HttpUrl(url)

    def get_tender_purchase_order_url(self, html: str) -> HttpUrl:
        """
        Get the URL of the purchase orders of a tender from the HTML content.
        """

        purchase_order_popup = self.get_href_by_element_id(html, "imgOrdenCompra")

        if not purchase_order_popup:
            raise ValueError("Purchase orders not found")

        match = re.search(r"qs=(.*)$", purchase_order_popup)

        if not match:
            raise ValueError("Purchase Order query string not found")

        qs = match.group(1)
        url = f"https://www.mercadopublico.cl/Procurement/Modules/RFB/PopUpListOC.aspx?qs={qs}"

        return HttpUrl(url)

    def get_purchase_orders_codes_from_html(self, html: str) -> List[str]:
        """
        Extract the purchase order codes from the HTML content.
        """

        codes = re.findall(r'id="(rptSearchOCDetail_ctl\d{2}_lkNumOC)"', html)

        return [self.get_text_by_element_id(html, xpath) for xpath in codes]

    def get_questions_url(self, html: str) -> HttpUrl:
        """
        Get the URL of the questions of a tender from the HTML content.
        """

        href = self.get_href_by_element_id(html, "imgPreguntasLicitacion")
        match = re.search(r"qs=(.*)$", href)

        if not match:
            raise ValueError("Questions query string not found")

        qs = match.group(1)
        url = f"https://www.mercadopublico.cl/Foros/Modules/FNormal/PopUps/PublicView.aspx?qs={qs}"

        return HttpUrl(url)

    def get_question_code(self, html: str) -> str:
        """
        Get the code of a question from the HTML content.
        """

        return self.get_value_by_element_id(html, "h_intRBFCode")

    def get_item_codes_from_html(self, html: str) -> List[str]:
        """
        Extract numerical codes from 'id' attributes in the HTML
        that match the pattern 'grvProducto_ctlXX_lblNumero'.

        We do this to identify the total number of
        products or services included in the tender.

        Args:
            html (str): The HTML content as a string.

        Returns:
            List[str]: A list of numerical codes (e.g., ['02', '03', '04']).
        """

        html_element: HtmlElement = self.get_html_element(html)

        # [
        #     "grvProducto_ctl02_lblNumero",
        #     "grvProducto_ctl03_lblNumero",
        #     "grvProducto_ctl04_lblNumero",
        #     "grvProducto_ctl05_lblNumero",
        #     "grvProducto_ctl06_lblNumero",
        #     "grvProducto_ctl07_lblNumero",
        #     "grvProducto_ctl08_lblNumero",
        # ]

        elements = html_element.xpath(
            "//@id[starts-with(., 'grvProducto_ctl') and contains(., '_lblNumero')]"
        )

        # ['02', '03', '04', '05', '06', '07', '08']
        return [
            match.group(1)
            for element in elements
            if (match := re.search(r"ctl(\d+)_lblNumero", element))
        ]

    def get_item_from_code(self, html: str, code: str) -> Item:
        """
        Get the item of a tender from its HTML content and code.
        """

        base_id = f"grvProducto_ctl{code}_lbl"

        index = self.get_text_by_element_id(html, f"{base_id}Numero")
        title = self.get_text_by_element_id(html, f"{base_id}Producto")
        category = self.get_text_by_element_id(html, f"{base_id}Categoria")
        description = self.get_text_by_element_id(html, f"{base_id}Descripcion")
        quantity = self.get_text_by_element_id(html, f"{base_id}Cantidad")
        unit = self.get_text_by_element_id(html, f"{base_id}Unidad")

        return Item(
            index=int(index),
            title=title,
            category=int(category),
            description=description,
            quantity=int(quantity),
            unit=Unit(unit),
        )

    def has_signed_base(self, html: str) -> bool:
        """
        Check if the tender has a signed base document.
        """

        if self.has_element_id(html, "descargar_pdf_baseFirmada"):
            return True

        return False
