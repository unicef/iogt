import re

class Shortcode:
    def __init__(self):
        self.shortcode_tags = {}

    def add_shortcode(self, tag, callback):
        if tag.strip() == '':
            raise Exception('Invalid shortcode name: Empty name given.')

        if re.search(r'[<>&/\[\]\x00-\x20=]', tag):
            reserved_chars = '& / < > [ ] ='
            raise Exception(f"Invalid shortcode name: {tag}. Do not use spaces or reserved characters: {reserved_chars}")

        self.shortcode_tags[tag] = callback

    def do_shortcode(self, content, ignore_html=False):
        shortcode_tags = self.shortcode_tags

        if '[' not in content:
            return content

        if not shortcode_tags or not isinstance(shortcode_tags, dict):
            return content

        def do_shortcode_tag(m):
            tag = m.group(2)
            attr = self.shortcode_parse_atts(m.group(3))
            content = m.group(5) if m.group(5) is not None else None
            output = m.group(1) + shortcode_tags[tag](attr, content) + m.group(6)
            return output

        matches = re.findall(r'\[([^<>&/\[\]\x00-\x20=]+)', content)
        tagnames = [tag for tag in matches if tag in shortcode_tags]
        
        pattern = self.get_shortcode_regex(tagnames)
        content = re.sub(pattern, do_shortcode_tag, content)

        return content

    def get_shortcode_regex(self, tagnames=None):
        shortcode_tags = self.shortcode_tags

        if not tagnames:
            tagnames = list(shortcode_tags.keys())

        tagregexp = '|'.join(map(re.escape, tagnames))
        
        return (
            r'\['                               # Opening bracket.
            r'(\[?)'                            # 1: Optional second opening bracket for escaping shortcodes: [[tag]].
            f'({tagregexp})'                    # 2: Shortcode name.
            r'(?![\w-])'                        # Not followed by word character or hyphen.
            r'('                                # 3: Unroll the loop: Inside the opening shortcode tag.
                r'[^\]\/]*'                     # Not a closing bracket or forward slash.
                r'(?:'
                    r'\/(?!])'                  # A forward slash not followed by a closing bracket.
                    r'[^\]\/]*'                 # Not a closing bracket or forward slash.
                r')*?'
            r')'
            r'(?:'
                r'(\/)'                         # 4: Self closing tag...
                r'\]'                           # ...and closing bracket.
            r'|'
                r'\]'                           # Closing bracket.
                r'(?:'
                    r'('                        # 5: Unroll the loop: Optionally, anything between the opening and closing shortcode tags.
                        r'[^[]*'                # Not an opening bracket.
                        r'(?:'
                            r'\[(?!\/\2\])'     # An opening bracket not followed by the closing shortcode tag.
                            r'[^[]*'            # Not an opening bracket.
                        r')*'
                    r')'
                    r'\[\/\2\]'                 # Closing shortcode tag.
                r')?'
            r')'
            r'(\]?)'                            # 6: Optional second closing bracket for escaping shortcodes: [[tag]].
        )

    def get_shortcode_atts_regex(self):
        return (
            r'([\w-]+)\s*=\s*"([^"]*)"(?:\s|$)'
            r'|([\w-]+)\s*=\s*\'([^\']*)\'(?:\s|$)'
            r'|([\w-]+)\s*=\s*([^\s\'"]+)(?:\s|$)'
            r'|"([^"]*)"(?:\s|$)'
            r'|\'([^\']*)\'(?:\s|$)'
            r'|(\S+)(?:\s|$)'
        )

    def shortcode_parse_atts(self, text):
        atts = {}
        pattern = self.get_shortcode_atts_regex()
        # text = re.sub(r'[\x00a0\x200b]+', ' ', text)
        matches = re.findall(pattern, text)
        
        for m in matches:
            if m[0]:
                atts[m[0].lower()] = m[1]
            elif m[2]:
                atts[m[2].lower()] = m[3]
            elif m[4]:
                atts[m[4].lower()] = m[5]
            elif m[6]:
                atts[m[6].lower()] = m[6]
            elif m[7]:
                atts[m[7].lower()] = m[7]
            elif m[8]:
                atts[m[8].lower()] = m[8]
        for key, value in atts.items():
            if '<' in value:
                if not re.match(r'^[^<]*+(?:<[^>]*+>[^<]*+)*+$', value):
                    atts[key] = ''
        return atts
