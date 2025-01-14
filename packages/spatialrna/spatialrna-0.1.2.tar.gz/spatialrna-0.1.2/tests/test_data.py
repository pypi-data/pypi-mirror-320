import os
import pytest
from spatialrna.spatialrna import SpatialRNA
import pandas as pd
from shutil import rmtree

def create_test_data():
    # Create a sample dataset for testing
    data = {
        "gene": ["gene1", "gene1", "gene2", "gene3", "gene3", "gene3"],
        "x": [1, 1, 2, 2, 2.5,8],
        "y": [1, 2.0, 1, 1, 2.5,3],
    }
    df = pd.DataFrame(data)
    os.makedirs("data/test_sample/raw", exist_ok=True)
    df.to_csv("data/test_sample/raw/test_sample.csv", index=False)
    return None

def clean_test_data():
    if os.path.exists("data/test_sample/"):
        rmtree("data/test_sample/")
clean_test_data()

def test_initialization():
    create_test_data()
    dataset = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.0,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        load_type="tile",
        process_tile_ids=[0],
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=False
    )
    assert dataset.num_tiles == 2
    assert dataset.radius_r == 1.0
    assert dataset.tile_by_dim == "y"
    assert dataset.process_tile_ids == [0]
    assert dataset.load_type == "tile"
    assert dataset.process_mode == "tile"
    assert dataset.load_tile_id == 0    

    clean_test_data()

def test_load_blank():
    create_test_data()
    dataset = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.0,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        load_type="blank",
        process_tile_ids=[0],
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=False
    )
    clean_test_data()
    assert dataset[0] is None

def test_load_when_not_process():
    create_test_data()
    dataset2 = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        process_mode="tile",
        radius_r=1.0,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        load_type="tile",
        load_tile_id=1,
        process_tile_ids=[0],
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=False
    )
    assert dataset2[0] is None
    clean_test_data()

def test_new_process_id():
    create_test_data()
    dataset1 = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.0,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        load_type="blank",
        process_mode="tile",
        process_tile_ids=[0],
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=False
    )
    ## tile 0 was processed but tile 1 has not. 
    print(os.listdir("data/test_sample/processed"))
    assert not os.path.exists("data/test_sample/processed/test_sample_data_tile1.pt")
    assert os.path.exists("data/test_sample/processed/test_sample_data_tile0.pt")
    dataset2 = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.0,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        load_type="tile",
        process_mode="tile",
        process_tile_ids=[1],
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=False
    )
    assert os.path.exists("data/test_sample/processed/test_sample_data_tile1.pt")

    clean_test_data()

def test_tile_by_dim_y():
    # Test the tile_by_dim, x or y method
    create_test_data()

    dataset = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.0,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        load_type="tile",
        load_tile_id=0,
        pad_hops = 0,
        process_tile_ids=[0],
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=False
    )
    assert dataset.tile_by_dim == "y"
    assert dataset.radius_r == 1.0
    assert dataset[0].x.size()[0] == 4
    clean_test_data()


def test_tile_by_dim_x():
    # Test the tile_by_dim, x or y method
    create_test_data()

    dataset = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.0,
        tile_by_dim="x",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        load_type="tile",
        load_tile_id=0,
        process_tile_ids=[0],
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=False
    )
    assert dataset.tile_by_dim == "x"
    assert dataset.radius_r == 1.0
    assert dataset[0].x.size()[0] == 5
    clean_test_data()


## one tile = no tiling 
def test_one_tile():
    create_test_data()
    dataset = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.0,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=1,
        load_type="tile",
        process_tile_ids=[0],
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=False
    )
    print(dataset[0].x)
    print(dataset[0].edge_index.shape)
    print(dataset[0].edge_index[0])
    print(dataset[0].edge_index[1])
    assert dataset[0].x.size()[0] == 6
    assert dataset[0].edge_index.size()[0] == 2
    assert dataset[0].edge_index.size()[1] == 2
    clean_test_data()


## one tile = no tiling ie. entire tissue region as one tile.
## radius_r is non-inclusive
def test_one_tile_r11():
    create_test_data()
    dataset = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.1,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=1,
        load_type="tile",
        process_tile_ids=[0],
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=False
    )
    print(dataset[0].x)
    print(dataset[0].edge_index.size)
    
    print(dataset[0].edge_index[0])
    print(dataset[0].edge_index[1])
    assert dataset[0].x.size()[0] == 6
    assert dataset[0].edge_index.size()[1] == 8
    assert dataset[0].edge_index.size()[0] == 2
    clean_test_data()