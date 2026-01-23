import os
import tempfile

import staticpipes.build_directory
import staticpipes.config
import staticpipes.worker

import datatig.staticpipes.pipes.datatig_write_staticsite_output
import datatig.staticpipes.pipes.load_datatig


def test_static_subdir():
    # setup
    out_dir = tempfile.mkdtemp(prefix="staticpipes_tests_")
    config = staticpipes.config.Config(
        pipes=[
            datatig.staticpipes.pipes.load_datatig.PipeLoadDatatig(),
            datatig.staticpipes.pipes.datatig_write_staticsite_output.PipeDatatigStaticSite(  # noqa
                output_dir="datatig"
            ),
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
    assert os.path.exists(os.path.join(out_dir, "datatig", "index.html"))
    with open(os.path.join(out_dir, "datatig", "index.html")) as fp:
        assert '<a href="/datatig/errors.html"' in fp.read()


def test_static_root():
    # setup
    out_dir = tempfile.mkdtemp(prefix="staticpipes_tests_")
    config = staticpipes.config.Config(
        pipes=[
            datatig.staticpipes.pipes.load_datatig.PipeLoadDatatig(),
            datatig.staticpipes.pipes.datatig_write_staticsite_output.PipeDatatigStaticSite(),  # noqa
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
    assert os.path.exists(os.path.join(out_dir, "index.html"))
    with open(os.path.join(out_dir, "index.html")) as fp:
        assert '<a href="/errors.html"' in fp.read()
