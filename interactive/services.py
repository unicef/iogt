from interactive.shortcode import Shortcode


class ShortCodeService:

    def apply_shortcode(self, content):
        shortcode_service = Shortcode()

        shortcode_service.add_shortcode('insert_message', self.message_callback)
        shortcode_service.add_shortcode('insert_button', self.button_callback)
        shortcode_service.add_shortcode('insert_form_field', self.form_callback)
        shortcode_service.add_shortcode('insert_image', self.image_callback)
        # shortcode_service.add_shortcode('insert_attachment_image', attachment_callback)
        shortcode_service.add_shortcode('insert_header', self.header_callback)
        shortcode_service.add_shortcode('insert_navbar', self.navbar_callback)
        shortcode_service.add_shortcode('insert_html', self.html_callback)
        shortcode_service.add_shortcode('insert_bg_color', self.header_callback)
        shortcode_service.add_shortcode('CONTINUE', lambda attrs, content=None: '')
        shortcode_service.add_shortcode('insert_trick_button', self.trick_button_callback)
        shortcode_service.add_shortcode('insert_progress', self.progress_callback)

        return shortcode_service.do_shortcode(content)

    def message_callback(self, attrs, content):
        return f'<p class="interactive-vaccine-text">{content}</p>'

    def button_callback(self, attrs, content):
        type = attrs.get("type", "submit")
        message = attrs.get("message", content)
        return f'<button type="{type}" class="interactive-btn" name="text" value="{message}">{content}</button>'

    def form_callback(self, attrs, content):
        if attrs['type'] == 'input':
            return f'<input class="text-input" type="text" name="text">'

        return ''

    def image_callback(self, attrs, content):
        class_value = attrs.get('class', '')
        width_value = attrs.get('width', '150')
        height_value = attrs.get('height', '')
        return f'<img src="{content}" class="{class_value}" width="{width_value}" height="{height_value}">'

    def header_callback(self, attrs, content=None):
        button_html = ''
        trigger_string = attrs.get('trigger_string', '')
        button_text = attrs.get('button_text', '')
        if button_text:
            button_html = f'<button type="submit" name="text" value="{trigger_string}">{button_text}</button>'

        return f'<div class="top-navbar"> <div>{content}</div> {button_html}  </div>'

    def html_callback(self, attrs, content):
        return content

    def navbar_callback(self, attrs, content=None):
        button_group = ''
        for x, y in attrs.items():
            button = '''<button type="submit" name="text" value="{0}">
                <div>
                    <i class="fa fa-house"></i>
                    <span>{1}</span>
                </div>
            </button>'''

            button_group += button.format(y, x.capitalize())

        return f'<section class="interactive_navigation">{button_group}</section>'

    def trick_button_callback(self, attrs, content=None):
        image = attrs.get("img", "")
        hint = attrs.get("hint", "")
        status = attrs.get("status", "unlocked")
        lock_img = attrs.get('lock_img', '')

        if status == 'locked':
            lock_btn_html = f'<button class="sub-section denial-btn {status}" type="submit" name="text" value="">'
            lock_img_html = f'<img src="{lock_img}" alt="locked">'
        else:
            lock_btn_html = f'<button class="sub-section denial-btn {status}" type="submit" name="text" value="{content}">'
            lock_img_html = ''

        button = f'''{lock_btn_html}
                <div class="section-header">
                    <img height="30" src="{image}" width="30">
                    <p class="section-title">{content}</p>
                </div>
                <div class="img-holder">
                    {lock_img_html}
                </div>
            </button>'''

        if hint:
            hint = f'<p class="trick_hint"><b>Hint:</b> {hint}</p>'

        return button + hint

    def progress_callback(self, attrs, content):
        return f'''<div class="progress">
                    <progress max="100" value="{content}" />
                </div>'''
