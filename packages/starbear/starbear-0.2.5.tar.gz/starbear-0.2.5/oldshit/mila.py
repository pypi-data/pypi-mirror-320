import asyncio
import re

from fabric import Connection

from starbear import ClientWrap, H, bear

ex = """  JOBID     USER    PARTITION           NAME  ST START_TIME             TIME NODES CPUS TRES_PER_N MIN_MEM NODELIST (REASON) COMMENT
2756229 breuleuo long-cpu-eek    interactive   R 2023-01-24T14:23       0:28     1    2        N/A      2G rtx7 (None) (null)
"""


style = """
body {
    width: 800px;
    margin: auto;
}
.status {
    width: 100%;
    background: beige;
}
.error {
    color: red;
}
table {
    border: 1px solid black;
    border-collapse: collapse;
}
th, td {
    border-left: 1px solid black;
    border-right: 1px solid black;
}
"""


def loop(page, conn, results):
    def cancel(jobid, event):
        conn.run(f"scancel {jobid}")

    call = conn.run("squeue -u breuleuo")
    page[results].set(H.pre(call.stdout))
    lines = call.stdout.split("\n")
    jobs = [re.split(pattern=" +", string=line.strip()) for line in lines if line]

    table = H.table(H.tr(H.th(field) for field in jobs[0]))

    for fields in jobs[1:]:
        jobid = fields[0]
        row = H.tr(H.td(field) for field in fields)
        row = row(H.td(H.button("Cancel", onclick=ClientWrap(cancel, partial=jobid))))
        table = table(row)

    page[results].set(table)


@bear
async def app(page):
    page["head"].print(H.style(style))
    page.print(
        status := H.div["status"]("Connecting...").autoid(),
        results := H.div["results"]().autoid(),
    )

    conn = Connection("mila")
    conn.run("echo 'hello'")
    page[status].set("Connected!")

    while True:
        await asyncio.sleep(10)
        try:
            loop(page, conn, results)
        except Exception as exc:
            page[results].set(H.div["error"]("An error occurred", str(exc)))
