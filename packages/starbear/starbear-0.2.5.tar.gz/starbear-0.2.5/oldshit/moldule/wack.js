
export default class Wack {
    constructor(node, options) {
        this.node = node;
        this.x = options.x;
    }

    wooper(y) {
        return this.x * y;
    }
}
