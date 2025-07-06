from utils import get_path, logger, format_date
import os
import json
import fitz

class FormFiller:
    def __init__(self):
        self.template_path = get_path('template.pdf')
        self.tick_icon_path = get_path('tick.png')
        self.coordinates = self._load_coordinates()

    def _load_coordinates(self):
        coord_path = get_path('coordinates.json')
        try:
            with open(coord_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError as e:
            logger.error(f"Coordinates file Not Found at {coord_path}")
        except Exception as e:
            logger.error(f"Failed to load coordinates.json: {e}")
            return {}
    
    @staticmethod
    def insert_text(page, coordinates: dict, data):
        for field_name, coords in coordinates.items():
            value = data.get(field_name, None)
            if value:
                fontsize = 12
                if "contact" in field_name or "email" in field_name:
                    value = value.replace(" ", "")
                if 'dob' in field_name:
                    value = format_date(value)
                if len(value) > 19:
                    value = value.title()
                    fontsize = 10
                try:
                    page.insert_text(coords, value, fontsize=fontsize, color=(0.0, 0.4667, 0.8314))
                except Exception as e:
                    logger.error(f'Error inserting text at {coords}: {e}')
    
    @staticmethod
    def insert_images(page, images: dict, data):
        for field_name, rect_coords in images.items():
            image_path = data.get(field_name)
            if not image_path:
                logger.warning(f'Image path not found for {field_name}')
                
                continue
            try:
                rect = fitz.Rect(*rect_coords)
                page.insert_image(rect, filename=image_path)
            except Exception as e:
                logger.error(f'Error inserting image {field_name}: {e}')

    @staticmethod
    def insert_checkmarks(page, checkboxes: list, data):
        #chechboxes= {'field1': {'option1': [x, y], 'option2': [x, y]}, 'field2': {...},..}
        tick_path = get_path('tick.png')
        if not os.path.exists(tick_path):
            logger.error(f'Tick image not found at {tick_path}')
            return

        for field_name, options in checkboxes.items():
            #options: dict = {'opt1': [coords], 'opt2': [coords]}
            if field_name in data:
                try:
                    x, y = options.get(data.get(field_name))
                    rect = fitz.Rect(x, y - 15, x + 15, y + 15)
                    page.insert_image(rect, filename=tick_path)
                except Exception as e:
                    logger.error(f'Error inserting checkmark for {field_name}: {e}')
        
    def fill_page(self, doc, page_num, page_coordinates, data):
        """Fills a single page of the form with text, images, and checkmarks."""
        page = doc[page_num]
        logger.debug(f"Fillin page {page_num}")

        # Insert text fields
        if "text_fields" in page_coordinates:
            logger.debug(f"Filling Text fields")
            FormFiller.insert_text(page, page_coordinates['text_fields'], data)
            logger.debug(f"Filling Text fields completed")

        if "images" in page_coordinates:
            logger.debug(f"Inserting Images")
            FormFiller.insert_images(page, page_coordinates['images'], data)
            logger.debug(f"Inserting Images completed")

        if "checkboxes" in page_coordinates:
            logger.debug(f"Filling Checkboxes")
            FormFiller.insert_checkmarks(page, page_coordinates['checkboxes'], data)
            logger.debug(f"Filling Checkboxes completed")


    def fill(self, player_data: dict, output_path: str):
        """Fill the form template with player data and save as PDF."""
        try:
            logger.debug(f"Opening template {self.template_path}")
            doc = fitz.open(self.template_path)
            

            for page_number, page_coordinates in enumerate(self.coordinates.get('pages',[])):
                self.fill_page(doc, page_number, page_coordinates, player_data)

            # Save filled form
            doc.save(output_path)
            logger.debug(f"Saved: {output_path}")
        except Exception as e:
            logger.error(f"Error filling form: {e}")

if __name__ == "__main__":
    ff = FormFiller()
    ff.fill(
        {'playersname': 'DARAM NIKHIL REDDY', 'playerdob': '04/04/2015', 'gender': 'male', 'playercrsid': '1234567890', 'fulladdress1': 'FLAT NO A-506, MURARI GIRIDHARI HOMES, BANDALAGUDA JAGIR, TELANGANA 500086', 'emailid1': 'LAKSHMIKANTH.DARAM@GMAIL.COM', 'contactno1': '9502428425', 'parentsname': 'DARAM, LAKSHMIKANTHA REDDY', 'fulladdress2': 'FLAT NO A-506, MURARI GIRIDHARI HOMES, BANDALAGUDA JAGIR, TELANGANA 500086', 'emailid2': 'LAKSHMIKANTH.DARAM@GMAIL.COM', 'contactno2': '9502428425', 'formerclubname': '', 'formerstateassociation': '', 'parentsrelationship': 'FATHER'},
        'out.pdf'
    )
