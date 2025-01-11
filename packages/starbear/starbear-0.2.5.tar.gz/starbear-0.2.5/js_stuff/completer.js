
class OptionPicker {
    constructor(settings) {
        this.controller = settings.controller;
        this.element = settings.element;
        this.submit = settings.submit;
        if (settings.reverse) {
            this.element.style.display = "flex";
            this.element.style["flex-direction"] = "column-reverse";
            this.goUp = this.goNext;
            this.goDown = this.goPrevious;
        }
        else {
            this.goUp = this.goPrevious;
            this.goDown = this.goNext;      
        }
        this.controller.onkeydown = evt => {
            switch (evt.key) {
                case "ArrowUp":
                this.goUp(evt.shiftKey);
                evt.preventDefault();
                break;
                case "ArrowDown":
                this.goDown(evt.shiftKey);
                evt.preventDefault();
                break;
                case "Enter":
                this.submit(this.selection());
                evt.preventDefault();
                break;
            }
        }
        this.cursors = [];
    }
    
    reset(newChildren) {
        this.element.innerHTML = "";
        for (let child of newChildren) {
            this.element.appendChild(child);
        }
        this.cursors = [];
    }
    
    goNext(expand) {
        const x = this.cursors.length - 1;
        if (!this.cursors.length && this.element.children.length) {
            this.setCursor(0);
        }
        else if (this.cursors.length) {
            const pos = Math.min(this.element.children.length - 1, this.cursors[x] + 1);
            if (expand) {
                this.addCursor(pos);
            }
            else {
                this.setCursor(pos);
            }
        }
    }
    
    goPrevious(expand) {
        if (!this.cursors.length && this.element.children.length) {
            this.setCursor(0);
        }
        else if (this.cursors.length) {
            const pos = Math.max(0, this.cursors[0] - 1);
            if (expand) {
                this.addCursor(pos);
            }
            else {
                this.setCursor(pos);
            }
        }
    }
    
    setCursor(value) {
        let new_cursors = [value];
        this.updateCursors(new_cursors);
    }
    
    addCursor(value) {
        let new_cursors = [value, ...this.cursors];
        new_cursors = [...new Set(new_cursors)];
        new_cursors.sort((x, y) => x - y);
        this.updateCursors(new_cursors);
    }
    
    updateCursors(new_cursors) {
        const n = this.element.children.length;
        if (n === 0) {
            return;
        }
        for (const cursor of this.cursors) {
            if (new_cursors.indexOf(cursor) === -1) {
                this.element.children[cursor].classList.remove("snek-popup-nav-cursor");
            }
        }
        for (const cursor of new_cursors) {
            const elem = this.element.children[cursor];
            elem.classList.add("snek-popup-nav-cursor");
            elem.scrollIntoView({block: "nearest", inline: "nearest"});
        }
        this.cursors = new_cursors;
    }
    
    selection() {
        let lines = [];
        for (const cursor of this.cursors) {
            let elem = this.element.childNodes[cursor];
            let attr = elem.getAttribute("selection-value");
            lines.push(attr || elem.innerText);
        }
        return lines;
    }
}

class AutoComplete {
    constructor(settings) {
        this.input = settings.input;
        this.completions = settings.completions;
        this.picker = new OptionPicker({
            controller: this.input,
            element: settings.complete_box,
            reverse: settings.reverse,
            submit: lines => {
                this.input.value = lines.join("\n");
            }
        });
        this.getList = settings.getList;
        this.input.oninput = evt => {
            let data = this.completions(this.input.value);
            this.picker.reset(data);
        }
    }
}

new AutoComplete({
    input: document.getElementById("wow"),
    complete_box: document.getElementById("radical"),
    reverse: false,
    completions: text => {
        let data = [];
        for (let i = 1; i < 5; i++) {
            const li = document.createElement("li");
            //li.innerHTML = text.repeat(i);
            li.setAttribute("selection-value", text.repeat(i));
            li.innerText = `${i} times ${text}`;
            data.push(li);
        }
        return data;
    }
});

new OptionPicker({
    controller: document.getElementById("innie"),
    element: document.getElementById("targ"),
    reverse: true,
});
