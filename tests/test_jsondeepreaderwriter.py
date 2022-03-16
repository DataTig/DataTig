from datatig.jsondeepreaderwriter import JSONDeepReaderWriter


def test_read_root_key():
    obj = JSONDeepReaderWriter({"cat": "Miaow", "dog": "woof"})
    assert obj.read("cat") == "Miaow"


def test_read_level1_all_keys():
    obj = JSONDeepReaderWriter(
        {
            "cat": {
                "noise": "Miaow",
                "tail": True,
            },
            "dog": "woof",
        }
    )
    assert obj.read("cat/noise") == "Miaow"
    assert obj.read("cat/tail") == True


def test_write_root_key():
    obj = JSONDeepReaderWriter({})
    obj.write("cat", "Miaow")
    assert {"cat": "Miaow"} == obj.get_json()


def test_write_level1():
    obj = JSONDeepReaderWriter({})
    obj.write("cat/noise", "Miaow")
    obj.write("cat/tail", "True")
    obj.write("cat/swims", None)
    assert {
        "cat": {
            "tail": "True",
            "noise": "Miaow",
            "swims": None,
        }
    } == obj.get_json()
