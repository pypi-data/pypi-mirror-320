## How does it differ from X?

Starbear differs from frameworks such as Streamlit or Plotly Dash by being more low-level and not trying to hide JavaScript. For example, Starbear has no special components: everything you are constructing is normal HTML. It comes with no special CSS and does not care about your project structure. It is also more on the imperative side, which can be a plus or a minus depending on who you ask.

What Starbear *does* do is some magick to allow passing arbitrary Python functions and queues as event handlers, or passing them to any JavaScript code. They are just turned into async functions in the browser, so they are are very few restrictions. This means that any existing JavaScript library can be integrated into Starbear apps, usually with no wrapping whatsoever. You can embed a CodeMirror editor to live edit Python code, a Plotly plot or Cytoscape graph that calls a Python function server-side whenever a point is clicked, and so on.

In a nutshell:

* If you like or need Python, but you are familiar/comfortable with web technology, you will like Starbear, because you will have very little to learn, and everything Starbear does will make your life way easier.
* If you don't find functional or declarative programming super intuitive (don't worry, I won't tell anyone) and you just want to shove stuff into divs, you will like Starbear.


