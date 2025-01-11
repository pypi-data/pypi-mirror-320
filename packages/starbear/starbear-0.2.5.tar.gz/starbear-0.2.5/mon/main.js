// import monaco from "./monaco.js";
import * as monaco from "./monaco.js";
import sheet1 from "./monaco.css" assert { type: "css" };
import sheet2 from "./style.css" assert { type: "css" };

document.adoptedStyleSheets = [...document.adoptedStyleSheets, sheet1, sheet2];

// export default monaco;


const KM = monaco.KeyMod;
const KC = monaco.KeyCode;


function debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}


class LiveEditor {
    constructor(element, options) {
        this.element = element;
        this.options = options;
        this.content = options.content;
        console.log(this.options);

        this.setupElement();
        this.setupEditor();
        this.inferStatus();

        if (this.options.autofocus) {
            this.editor.focus();
        }
    }

    setupElement() {
        let container = document.createElement("div");
        container.className = "snek-bedit-editor snek-editor-cyclable"
        container.onclick = () => {}
        // container.onkeydown = e => {
        //     e.stopPropagation();
        // }
        this.container = container

        let status = document.createElement("div");
        status.className = "snek-bedit-status"

        let status_filename = document.createElement("div");
        status_filename.className = "snek-bedit-filename"
        status_filename.innerText = this.options.filename;

        let status_state = document.createElement("div");
        status_state.className = "snek-bedit-state"
        status_state.innerText = "live, saved on disk"
        this.status_state = status_state;

        status.appendChild(status_filename)
        status.appendChild(status_state)

        this.element.appendChild(container);
        this.element.appendChild(status);
    }

    inferStatus() {
        let curr = this.editor.getValue();
        if (curr === this.content.live) {
            if (curr === this.content.saved) {
                this.setStatus("saved");
            }
            else {
                this.setStatus("live");
            }
        }
        else {
            this.setStatus("dirty");
        }
    }

    setStatus(status, message) {
        this.status = status;
        this.element.className = "snek-bedit snek-bedit-" + status;
        if (status === "saved") {
            this.status_state.innerText = message || "live, saved on disk";
        }
        else if (status === "live") {
            this.status_state.innerText = message || "live, not saved";
        }
        else if (status === "dirty") {
            this.status_state.innerText = message || "modified";
        }
        else if (status === "error") {
            this.status_state.innerText = message || "error";
        }
    }

    async communicate(method) {
        try {
            // let method = commit ? "commit" : "save";
            let value = this.editor.getValue();
            let cb = this.options.callbacks[method];
            if (!cb) {
                return false;
            }
            let response = await cb(value);
            if (response === true) {
                this.content.live = value
                if (method === "commit") {
                    this.content.saved = value
                }
                this.inferStatus();
            }
            return true;
        }
        catch(exc) {
            let message = (
                exc.type === "InvalidSourceException"
                ? exc.message
                : `${exc.type}: ${exc.message}`
            );
            this.setStatus("error", message);
            return false;
        }
    }

    setupEditor() {
        this.editor = monaco.editor.create(this.container, {
            value: this.content.live,
            language: 'python',
            lineNumbers: false,
            minimap: {enabled: false},
            scrollBeyondLastLine: false,
            overviewRulerLanes: 0,
            folding: false,
            automaticLayout: true,
        });
        this.container.$editor = this.editor;

        if (this.options.resize) {
            this.editor.onDidContentSizeChange(this.event_updateHeight.bind(this));
            this.event_updateHeight();
        }

        this.editor.addCommand(
            KM.CtrlCmd | KC.KeyS,
            this.command_save.bind(this)
        );
        this.editor.addCommand(
            KM.CtrlCmd | KM.Shift | KC.KeyS,
            this.command_commit.bind(this)
        );
        this.editor.addCommand(
            KM.WinCtrl | KC.Enter,
            this.command_save_and_repl.bind(this)
        );
        this.editor.addCommand(
            KM.WinCtrl | KM.Shift | KC.Enter,
            this.command_commit_and_repl.bind(this)
        );
        this.editor.addCommand(
            KM.CtrlCmd | KC.KeyR,
            this.command_reset_to_saved.bind(this)
        );

        if (this.options.highlight !== null && this.options.highlight !== undefined) {
            var hl = this.editor.deltaDecorations([], [
                { range: new monaco.Range(this.options.highlight + 1,1,this.options.highlight + 1,1), options: { isWholeLine: true, className: 'snek-bedit-hl' }},
            ]);
            this.editor.revealLineInCenter(this.options.highlight + 1);
            this.editor.getModel().onDidChangeContent(
                () => {
                    hl = this.editor.deltaDecorations(hl, []);
                }
            )
        }

        this.editor.getModel().onDidChangeContent(
            () => {
                if (this.status !== "error") {
                    this.inferStatus();
                }
            }
        )
        this.editor.getModel().onDidChangeContent(
            debounce(this.command_update.bind(this))
        )
    }

    event_updateHeight() {
        const contentHeight = Math.min(
            this.options.max_height || 500,
            this.editor.getContentHeight()
        );
        this.container.style.height = `${contentHeight}px`;
        // Normally the relayout should be automatic, but doing it here
        // avoids some flickering
        this.editor.layout({
            width: this.container.offsetWidth - 10,
            height: contentHeight
        });
    }

    focus_repl() {
        // repl.mainRepl.editor.focus();
    }

    async command_update() {
        await this.communicate("update");
    }

    async command_save() {
        await this.communicate("save");
    }
    
    async command_commit() {
        await this.communicate("commit");
    }

    async command_save_and_repl() {
        if (await this.communicate("save")) {
            this.focus_repl();
        }
    }
    
    async command_commit_and_repl() {
        if (await this.communicate("commit")) {
            this.focus_repl();
        }
    }

    async command_reset_to_saved() {
        this.editor.setValue(this.content.saved);
        this.inferStatus();
    }
}

export default LiveEditor;
