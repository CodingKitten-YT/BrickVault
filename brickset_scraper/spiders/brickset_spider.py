import scrapy
import os
import json

class BricksetSpider(scrapy.Spider):
    name = "brickset"
    allowed_domains = ["brickset.com"]
    start_urls = ['https://brickset.com/browse/parts']

    def parse(self, response):
        # Find the "Colours" section
        colours_section = response.xpath('//section[div/h1/text()="Colours"]')
        colour_links = colours_section.xpath('.//a')
        for link in colour_links:
            colour_name = link.xpath('text()').get().split(' (')[0]
            colour_url = response.urljoin(link.xpath('@href').get())
            yield scrapy.Request(url=colour_url, callback=self.parse_colour, meta={'colour_name': colour_name})

    def parse_colour(self, response):
        colour_name = response.meta['colour_name']
        bricks = []
        brick_elements = response.xpath('//article[@class="set"]')

        for brick_element in brick_elements:
            brick_info = {
                'name': brick_element.xpath('.//h1/a/text()').get().strip(),
                'part_number': brick_element.xpath('.//div[@class="tags"]/a[1]/text()').get().strip(),
                'image_url': brick_element.xpath('.//a[@class="highslide plain mainimg"]/img/@src').get().strip(),
                'tags': brick_element.xpath('.//div[@class="tags"]/a/text()').getall()
            }
            # Skip "Date added"
            brick_info['tags'] = [tag for tag in brick_info['tags'] if "Date added" not in tag]
            # Extract additional meta data, skip "Date added"
            meta_sections = brick_element.xpath('.//div[@class="meta"]/dl/dt')
            for section in meta_sections:
                section_title = section.xpath('text()').get().strip()
                if section_title == "Date added":
                    continue
                brick_info[section_title] = section.xpath('following-sibling::dd[1]/text()').get().strip()
            bricks.append(brick_info)

        # Save the bricks for this colour
        os.makedirs('lego_bricks', exist_ok=True)
        filename = f'lego_bricks/{colour_name.replace(" ", "_")}.json'
        with open(filename, 'w') as f:
            json.dump(bricks, f, indent=4)

        # Handle pagination
        next_page = response.xpath('//a[@title="Next"]/@href').get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse_colour, meta={'colour_name': colour_name})

        # Collect all bricks data
        yield {
            'colour_name': colour_name,
            'bricks': bricks
        }