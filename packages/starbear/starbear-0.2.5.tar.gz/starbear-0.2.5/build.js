import { Idiomorph } from "https://cdn.jsdelivr.net/npm/idiomorph@0.3.0/dist/idiomorph.esm.js";

export default class Form {
    constructor(element, options) {
        this.element = element;
        this.oninput = options.oninput;
        this.prepare();
    }

    getElement() {
        return this.element;
    }

    set(newElement) {
        Idiomorph.morph(this.element, newElement, {ignoreActiveValue: true});
        this.prepare();
    }

    findPath(element) {
        let pth = []
        do {
            let ref = element.getAttribute("--ref");
            let represents = element.getAttribute("represents");
            if (represents !== null) {
                pth.unshift(...represents.split("."));
            }
            if (ref) {
                ref = {"%": "Reference", id: Number(ref.split("#")[1])};
                return [ref, pth];
            }
            element = element.parentNode;
        } while (element.parentNode && element !== this.element)

        return [null, pth]
    }

    send(element, value) {
        let [ref, pth] = this.findPath(element);
        let rval = value;
        pth.reverse();
        for (let key of pth) {
            rval = {[key]: rval};
        }
        this.oninput([ref, rval]);
    }

    listenTo(node) {
        if (node.__listened) { return; }
        if (node.tagName === "INPUT") {
            node.addEventListener("input", e => this.send(e.target, e.target.type === "checkbox" ? e.target.checked : e.target.value));
        }
        node.__listened = true;
    }

    prepare() {
        for (let node of this.element.querySelectorAll("[represents]")) {
            this.listenTo(node);
        }
    }
}
