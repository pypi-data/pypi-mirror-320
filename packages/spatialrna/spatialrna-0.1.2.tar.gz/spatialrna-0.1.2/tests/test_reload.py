import os
import pytest
from spatialrna.spatialrna import SpatialRNA
import pandas as pd
from shutil import rmtree
from torch_geometric.sampler import NegativeSampling

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

def test_force_reload():
    clean_test_data()
    create_test_data()
    # process mode with subgraph, tile graph will be created by init (after checking force_reload, etc)
    # try:
    dataset = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.1,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        load_type="blank",
        load_tile_id=0,
        process_tile_ids=[0,1],
        process_mode="subgraph",
        subgraph_mode="link_based",
        num_sampled_edges=2,
        num_neighbors = [-1,-1],
        batch_size = 4,
        neg_sampling = NegativeSampling(mode="triplet",amount=1),
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=True
    )
    time_stamp1 = os.path.getmtime("data/test_sample/processed/test_sample_data_tile1.pt")
    import time
    time.sleep(3)
    # force_reload controls only the re-processing of data_tile.pt 
    SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.1,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        force_reload=True,
        load_type="blank",
        load_tile_id=0,
        process_tile_ids=[0,1],
        process_mode="subgraph",
        subgraph_mode="link_based",
        num_sampled_edges=2,
        num_neighbors = [-1,-1],
        batch_size = 4,
        neg_sampling = NegativeSampling(mode="triplet",amount=1),
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=True
    )
    time_stamp2 = os.path.getmtime("data/test_sample/processed/test_sample_data_tile1.pt")
    assert time_stamp1 != time_stamp2


def test_force_resample():
    clean_test_data()
    create_test_data()
    # process mode with subgraph, tile graph will be created by init (after checking force_reload, etc)
    # try:
    dataset = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.1,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        load_type="blank",
        load_tile_id=0,
        process_tile_ids=[0,1],
        process_mode="subgraph",
        subgraph_mode="link_based",
        num_sampled_edges=2,
        num_neighbors = [-1,-1],
        batch_size = 4,
        neg_sampling = NegativeSampling(mode="triplet",amount=1),
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=True
    )
    time_stamp1_tile1 = os.path.getmtime("data/test_sample/processed/test_sample_data_tile1.pt")
    time_stamp1_subgraph_tile1 = os.path.getmtime("data/test_sample/subgraph/test_sample_subgraph_data_tile1.pt")

    import time
    time.sleep(3)

    # force_resample controls only the re-sampling of subgraphs from data_tile.pt 
    SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.1,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        force_reload=False,
        force_resample=True,
        load_type="blank",
        load_tile_id=0,
        process_tile_ids=[0,1],
        process_mode="subgraph",
        subgraph_mode="link_based",
        num_sampled_edges=2,
        num_neighbors = [-1,-1],
        batch_size = 4,
        neg_sampling = NegativeSampling(mode="triplet",amount=1),
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=True
    )
    time_stamp2_tile1 = os.path.getmtime("data/test_sample/processed/test_sample_data_tile1.pt")
    time_stamp2_subgraph_tile1 = os.path.getmtime("data/test_sample/subgraph/test_sample_subgraph_data_tile1.pt")
    
    assert time_stamp1_tile1 == time_stamp2_tile1
    assert time_stamp1_subgraph_tile1 != time_stamp2_subgraph_tile1