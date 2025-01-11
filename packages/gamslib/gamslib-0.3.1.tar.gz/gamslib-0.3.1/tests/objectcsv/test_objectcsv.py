"""Tests for the objectcsv.objectcsv module."""

import copy
import csv
from dataclasses import asdict
from pathlib import Path

import pytest

from gamslib.objectcsv.objectcsv import (
    DatastreamsCSVFile,
    DSData,
    ObjectCSV,
    ObjectCSVFile,
    ObjectData,
)
from gamslib.objectcsv import defaultvalues


@pytest.fixture(name="objdata")
def objdata_fixture() -> ObjectData:
    "Return a ObjectData object."
    return ObjectData(
        recid="obj1",
        title="The title",
        project="The project",
        description="The description with ÄÖÜ",
        creator="The creator",
        rights="The rights",
        publisher="The publisher",
        source="The source",
        objectType="The objectType",
    )


@pytest.fixture(name="dsdata")
def dsdata_fixture() -> DSData:
    "Return a DSData object."
    return DSData(
        dspath="obj1/TEI.xml",
        dsid="TEI.xml",
        title="The TEI file with üßÄ",
        description="A TEI",
        mimetype="application/xml",
        creator="Foo Bar",
        rights="GPLv3",
        lang = "en de"
    )


@pytest.fixture(name="objcsvfile")
def objcsvfile_fixture(objdata: ObjectData, tmp_path: Path) -> Path:
    "Return path to an object.csv file from objdata"
    data = asdict(objdata)
    col_names = list(data.keys())
    csv_file = tmp_path / "obj1" / "object.csv"
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=col_names)
        writer.writeheader()
        writer.writerow(data)
    return csv_file


@pytest.fixture(name="dscsvfile")
def dscsvfile_fixture(dsdata: DSData, tmp_path: Path) -> Path:
    """Return path to a datastreams.csv file.

    Contains data from dsdata as first element and a copy of dsdata,
    where object id, dspath and dsid are different.
    """
    ds1 = asdict(dsdata)
    ds2 = copy.deepcopy(ds1)
    ds2["dspath"] = "obj2/TEI2.xml"
    ds2["dsid"] = "TEI2.xml"

    col_names = list(ds1.keys())

    csv_file = tmp_path / "obj1" / "datastreams.csv"
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=col_names)
        writer.writeheader()
        writer.writerow(ds1)
        writer.writerow(ds2)
    return csv_file


def test_objectdata_creation(objdata):
    "Should create an ObjectData object."
    assert objdata.recid == "obj1"
    assert objdata.title == "The title"
    assert objdata.project == "The project"
    assert objdata.description == "The description with ÄÖÜ"
    assert objdata.creator == "The creator"
    assert objdata.rights == "The rights"
    assert objdata.publisher == "The publisher"
    assert objdata.source == "The source"
    assert objdata.objectType == "The objectType"
    


def test_objectdata_validate(objdata):
    "Should raise an exception if required fields are missing."
    objdata.recid = ""
    with pytest.raises(ValueError):
        objdata.validate()
    objdata.recid = "obj1"
    objdata.title = ""
    with pytest.raises(ValueError):
        objdata.validate()
    objdata.title = "The title"
    objdata.rights = ""
    with pytest.raises(ValueError):
        objdata.validate()
    objdata.rights = "The rights"
    objdata.source = ""
    with pytest.raises(ValueError):
        objdata.validate()
    objdata.source = "The source"
    objdata.objectType = ""
    with pytest.raises(ValueError):
        objdata.validate()


def test_dsdata_creation(dsdata):
    "Should create a DSData object."
    assert dsdata.dspath == "obj1/TEI.xml"
    assert dsdata.dsid == "TEI.xml"
    assert dsdata.title == "The TEI file with üßÄ"
    assert dsdata.description == "A TEI"
    assert dsdata.mimetype == "application/xml"
    assert dsdata.creator == "Foo Bar"
    assert dsdata.rights == "GPLv3"
    assert dsdata.lang == "en de"

    # this is a @property

def test_ds_data_creation_with_missing_values():
    "Missing values should be added automatically."
    dsdata = DSData(
        dspath="obj1/DC.xml",
        dsid="DC.xml",
    )

    assert dsdata.title == defaultvalues.FILENAME_MAP["DC.xml"]["title"]
    assert dsdata.description == defaultvalues.FILENAME_MAP["DC.xml"]["description"]
    assert dsdata.mimetype == defaultvalues.DEFAULT_MIMETYPE
    assert dsdata.creator == defaultvalues.DEFAULT_CREATOR
    assert dsdata.rights == defaultvalues.DEFAULT_RIGHTS

    dsdata =  DSData(
        dspath="object1/TEI.xml",
        dsid="TEI.xml"
    )
    assert dsdata.title == defaultvalues.FILENAME_MAP["TEI.xml"]["title"]
    assert dsdata.description == defaultvalues.FILENAME_MAP["TEI.xml"]["description"]
    
    dsdata =  DSData(
        dspath="object1/LIDO.xml",
        dsid="LIDO.xml"
    )
    assert dsdata.title == defaultvalues.FILENAME_MAP["LIDO.xml"]["title"]
    assert dsdata.description == defaultvalues.FILENAME_MAP["LIDO.xml"]["description"]

    dsdata =  DSData(
        dspath="object1/RDF.xml",
        dsid="RDF.xml"
    )
    assert dsdata.title == defaultvalues.FILENAME_MAP["RDF.xml"]["title"]
    assert dsdata.description == defaultvalues.FILENAME_MAP["RDF.xml"]["description"]

    dsdata = DSData(
        dspath="object1/xy.png",
        dsid="xy.png",
        mimetype="image/png"
    )
    assert dsdata.title == "Image: xy.png" 

    dsdata = DSData(
        dspath="object1/xy.mp4",
        dsid="xy.mp4",
        mimetype="video/mp4"
    )
    assert dsdata.title == "Video: xy.mp4" 

    dsdata = DSData(
        dspath="object1/xy.mp3",
        dsid="xy.mp3",
        mimetype="audio/mpeg"
    )
    assert dsdata.title == "Audio: xy.mp3"


def test_dsdata_validate(dsdata):
    "Should raise an exception if required fields are missing."
    dsdata.dspath = ""
    with pytest.raises(ValueError):
        dsdata.validate()
    dsdata.dspath = "obj1/TEI.xml"
    dsdata.dsid = ""
    with pytest.raises(ValueError):
        dsdata.validate()
    dsdata.dsid = "TEI.xml"
    dsdata.mimetype = ""
    with pytest.raises(ValueError):
        dsdata.validate()
    dsdata.mimetype = "application/xml"
    dsdata.rights = ""
    with pytest.raises(ValueError):
        dsdata.validate()


def test_objectcsvfile(objcsvfile: Path, objdata: ObjectData):
    "Should create an ObjectCSVFile object from a csv file."
    ocf = ObjectCSVFile.from_csv(objcsvfile)
    result = list(ocf.get_data())
    assert len(result) == 1
    assert result[0] == objdata

    # test the get_data method with pid parameter, which should return the same result,
    # because we only have one object in the csv file
    result = list(ocf.get_data("obj1"))
    assert len(result) == 1
    assert result[0] == objdata

    # and the __len__method
    assert len(ocf) == 1

    # now save the object to a new csv file and compare the content
    csv_file = objcsvfile.parent / "object2.csv"
    ocf.to_csv(csv_file)
    assert objcsvfile.read_text() == csv_file.read_text()


def test_dscsvfile(dscsvfile: Path, dsdata: DSData):
    "Test the DatastreamsCSVFile object."
    dcf = DatastreamsCSVFile.from_csv(dscsvfile)
    result = list(dcf.get_data())
    assert len(result) == 2
    assert result[0].dspath == "obj1/TEI.xml"
    assert result[1].dspath == "obj2/TEI2.xml"

    # test the get_data method with pid parameter
    result = list(dcf.get_data("obj1"))
    assert len(result) == 1
    assert result[0] == dsdata

    result = list(dcf.get_data("obj2"))
    assert len(result) == 1

    # test the __len__ method
    assert len(dcf) == 2

    # now save the datastream.csv file to a new file and compare the content
    csv_file = dscsvfile.parent / "datastreams2.csv"
    dcf.to_csv(csv_file)
    assert dscsvfile.read_text(encoding="utf-8") == csv_file.read_text(encoding="utf-8")


def test_object_csv(
    objcsvfile: Path, dscsvfile: Path, tmp_path: Path):
    "Should create an ObjectCSV object."

    oc = ObjectCSV(objcsvfile.parent)
    assert len(oc.object_data) == 1
    assert len(oc.datastream_data) == 2
    assert oc.is_new() is False
    assert oc.object_id == "obj1"

    assert oc.count_objects() == 1
    assert oc.count_datastreams() == 2

    # test write
    objcsvfile.unlink()
    dscsvfile.unlink()
    oc.write()
    assert objcsvfile.exists()
    assert dscsvfile.exists()
    
    # test write with explicit filenames
    obj_csv = tmp_path / "o.csv"
    ds_csv = tmp_path / "d.csv"
    oc.write(obj_csv, ds_csv)
    assert obj_csv.exists()
    assert ds_csv.exists()
    assert obj_csv.read_text(encoding="utf-8") == objcsvfile.read_text(
        encoding="utf-8"
    )
    assert ds_csv.read_text(
        encoding="utf-8"
    ) == dscsvfile.read_text(encoding="utf-8")

    # test clear()
    oc.clear()
    assert oc.count_objects() == 0
    assert oc.count_datastreams() == 0


def test_object_csv_modify_get_set_data(
    objcsvfile: Path, dscsvfile: Path, objdata: ObjectData, dsdata: DSData
):
    "Test if adding and retrieving object and datastream data works."
    # test add_datastream() and get_datastreamdata()
    oc = ObjectCSV(objcsvfile.parent)

    # test adding a datastream
    new_ds = copy.deepcopy(dsdata)
    new_ds.dspath = "obj1/TEI3.xml"
    oc.add_datastream(new_ds)
    assert oc.count_datastreams() == 3
    assert len(list(oc.get_datastreamdata())) == 3
    assert list(oc.get_datastreamdata("obj1"))[-1] == new_ds

    # test add_objectdata() and get_objectdata()
    new_obj = copy.deepcopy(objdata)
    new_obj.recid = "obj2"
    oc.add_objectdata(new_obj)
    assert len(list(oc.get_objectdata())) == 2
    assert list(oc.get_objectdata("obj2"))[-1] == new_obj

    # test write() with overwriting the original csv files
    objcsvfile.unlink()
    dscsvfile.unlink()

    oc.write(objcsvfile, dscsvfile)

    assert objcsvfile.exists()
    assert dscsvfile.exists()


def test_object_csv_empty_dir(tmp_path):
    "The the is_new method with an empty directory."
    empty_oc = ObjectCSV(tmp_path)
    assert empty_oc.is_new()


def test_object_csv_missing_dir():
    "Should raise an exception if the directory does not exist."
    with pytest.raises(FileNotFoundError):
        ObjectCSV(Path("does_not_exist"))
