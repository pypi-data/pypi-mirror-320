
let currId = 0;

export default function quacko(f) {
    let id = currId++;
    let value = 0;
    let foo = event => {
        let delta = 1;
        if (event.metaKey) {
            delta = -1;
        }
        let old = value;
        value += delta;
        if (old === 0) {
            f({"%": "Quacko", id, value});
        }
        else {
            f({"%": "Quacko", id, delta});
        }
    }
    let div = document.createElement("div");
    div.innerText = "hello mom";
    div.addEventListener("click", foo);
    return div;
}
