from bs4 import BeautifulSoup


def get_all_renditions_urls(image):
    return [
        rendition.url
        for rendition
        in image.get_rendition_model().objects.filter(image_id=image.id)
    ]


def extract_urls_from_rich_text(text):
    return [
        img['src']
        for img
        in BeautifulSoup(str(text), 'lxml').find_all('img')
    ]


def collect_urls_from_streamfield(field):
    urls = []
    for block in field:
        if block.block_type == 'image':
            urls += get_all_renditions_urls(block.value)
        if block.block_type == 'paragraph':
            urls += extract_urls_from_rich_text(block.value)
        if block.block_type == 'download':
            urls += extract_urls_from_rich_text(
                block.value.get('description', '')
            )
        if block.block_type == 'media':
            urls.append(block.value.url)
    return urls
