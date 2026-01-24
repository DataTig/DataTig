import os
import tempfile

import staticpipes.build_directory
import staticpipes.config
import staticpipes.worker

import datatig.staticpipes.pipes.frictionless_zip
import datatig.staticpipes.pipes.load


def test_frictionless():
    # setup
    out_dir = tempfile.mkdtemp(prefix="staticpipes_tests_")
    config = staticpipes.config.Config(
        pipes=[
            datatig.staticpipes.pipes.load.PipeDataTigLoad(),
            datatig.staticpipes.pipes.frictionless_zip.PipeDataTigFrictionlessZip(),  # noqa
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
    assert os.path.exists(os.path.join(out_dir, "frictionless.zip"))
