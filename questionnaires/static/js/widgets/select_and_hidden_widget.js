// copied from wagtail
class BoundWidget {
    constructor(element, name, idForLabel, initialState) {
        var selector = ':input[name="' + name + '_0"]'; // hidden input selector
        this.input = element.find(selector).addBack(selector);  // find, including element itself
        this.idForLabel = idForLabel;
        this.setState(initialState);
    }
    getValue() {
        return this.input.val();
    }
    getState() {
        return this.input.val();
    }
    setState(state) {
        this.input.val(state);
    }
    getTextLabel(opts) {
        const val = this.getValue();
        if (typeof val !== 'string') return null;
        const maxLength = opts && opts.maxLength;
        if (maxLength && val.length > maxLength) {
            return val.substring(0, maxLength - 1) + '…';
        }
        return val;
    }
    focus() {
        this.input.focus();
    }
}

class SelectAndHiddenWidget {
    constructor(html, idPattern) {
        this.html = html;
        this.idPattern = idPattern;
    }

    boundWidgetClass = BoundWidget;

    render(placeholder, name, id, initialState) {
        var html = this.html.replace(/__NAME__/g, name).replace(/__ID__/g, id);
        var idForLabel = this.idPattern.replace(/__ID__/g, id);
        var dom = $(html);
        $(placeholder).replaceWith(dom);
        // eslint-disable-next-line new-cap
        return new this.boundWidgetClass(dom, name, idForLabel, initialState);
    }
}

window.telepath.register('questionnaires.widgets.SelectAndHiddenWidget', SelectAndHiddenWidget);
