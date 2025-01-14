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

def test_subgraph_mode_basic():
    create_test_data()
    SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.1,
        tile_by_dim="y",
        num_tiles=2,
        dim_x="x",
        dim_y="y",
        load_type="blank",
        pad_hops=0,
        process_tile_ids=[0,1],
        process_mode="tile",
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=False
    )
    assert os.path.exists("data/test_sample/processed/test_sample_data_tile0.pt")
    assert os.path.exists("data/test_sample/processed/test_sample_data_tile1.pt")
    # process mode with subgraph, when tile was not created, the tile graph will be created.
    clean_test_data()
    create_test_data()
    subgraphs = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=11,
        tile_by_dim="y",
        num_tiles=2,
        dim_x="x",
        dim_y="y",
        load_tile_id=1,
        load_type="subgraph",
        pad_hops=0,
        process_tile_ids=[1],
        process_mode="subgraph",
        subgraph_mode="link_based",
        num_sampled_edges=2,
        num_neighbors = [-1,-1],
        batch_size = 2,
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=False
    )
    assert not os.path.exists("data/test_sample/subgraph/test_sample_subgraph_data_tile0.pt")
    assert os.path.exists("data/test_sample/subgraph/test_sample_subgraph_data_tile1.pt")

    subgraphs = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=1.1,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        load_type="subgraph",
        load_tile_id=1,
        pad_hops=0,
        process_tile_ids=[0],
        process_mode="subgraph",
        subgraph_mode="node_based",
        force_resample=True,
        num_seed_nodes=2,
        num_neighbors = [-1,-1],
        num_walks=2,
        # batch_size = 2, batch size is inferred when subgraph mode is node_based with random walks
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=False
    )
    assert os.path.exists("data/test_sample/subgraph/test_sample_subgraph_data_tile0.pt")
    assert os.path.exists("data/test_sample/subgraph/test_sample_subgraph_data_tile1.pt")

    clean_test_data()


def test_subgraph_node_based():
    import shutil

    if os.path.exists("data/test_df/subgraph"):
        shutil.rmtree("data/test_df/subgraph")
    if os.path.exists("data/test_df/processed"):
        shutil.rmtree("data/test_df/processed")
    # the loaded subgraph data object is a list of 1
    subgraphs = SpatialRNA(
        root="data/test_df/",
        sample_name="test_df",
        radius_r=15,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        load_type="subgraph",
        load_tile_id=1,
        pad_hops=0,
        process_tile_ids=[0,1],
        process_mode="subgraph",
        subgraph_mode="node_based",
        force_resample=True,
        num_seed_nodes=4,
        num_neighbors = [-1,-1],
        subgraph_type= "bidirectional",
        num_walks=2,
        # batch_size = 2, batch size is inferred when subgraph mode is node_based with random walks
        one_hot_encoding={"A": 0, "B": 1, "C": 3},
        seed = 100,
        log=True
    )
    import torch
    assert subgraphs[0].x.size()[0] == 8
     #[3, 3, 0, 0, 1, 3, 3, 0]
    assert subgraphs[0].x[0] == 3 
    assert subgraphs[0].x[1] == 3 
    assert subgraphs[0].x[2] == 0 

    assert (subgraphs[0].edge_label_index.size()[1] == 8)
