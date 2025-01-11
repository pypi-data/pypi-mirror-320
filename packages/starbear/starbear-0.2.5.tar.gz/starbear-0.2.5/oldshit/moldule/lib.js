
// import cytoscape from 'cytoscape';

// export function make_graph(element, options) {
//     this.cy = cytoscape({
//         container: element,
//         elements: options.data,
//         style: options.style,
//         layout: {name: options.layout}
//     });
//     if (options.on_node) {
//         this.cy.on('click', 'node', function(evt){
//             options.on_node(evt.target.data());
//         });
//     }
// }

export default class Counter {
    constructor(node, options) {
        this.node = node;
        this.increment = options.increment;
        this.current = 0;
        this.node.innerText = "Click me!";
        this.node.onclick = async evt => {
            this.current += this.increment;
            this.node.innerText = this.current;
            await options.callback(this.current);
        }
    }
}
