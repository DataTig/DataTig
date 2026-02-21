import os
import tempfile

import staticpipes.build_directory
import staticpipes.config
import staticpipes.pipes.collection_records_process
import staticpipes.processes.jinja2
import staticpipes.worker

import datatig.staticpipes.pipes.load


def test_site_1():
    # setup
    out_dir = tempfile.mkdtemp(prefix="staticpipes_tests_")
    config = staticpipes.config.Config(
        pipes_and_groups_of_pipes=[
            datatig.staticpipes.pipes.load.PipeDataTigLoad(),
            staticpipes.pipes.collection_records_process.PipeCollectionRecordsProcess(
                collection_name="datas",
                processors=[
                    staticpipes.processes.jinja2.ProcessJinja2(
                        template="_templates/item.html"
                    )
                ],
            ),  # noqa
        ],
    )
    worker = staticpipes.worker.Worker(
        config,
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "fixtures",
            "site_1",
        ),
        out_dir,
    )
    # run
    worker.build()
    # test
    with open(os.path.join(out_dir, "datas", "1.html")) as fp:
        contents = fp.read()
    contents = "".join([i.strip() for i in contents.split("\n")])
    assert (
        "<!doctype html><html><head><title>Hello</title></head><body><h1>One</h1></body></html>"  # noqa
        == contents
    )
