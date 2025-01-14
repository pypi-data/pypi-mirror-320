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

def test_process_order_subgraph():
    clean_test_data()
    create_test_data()
    # process mode with subgraph, tile graph will be created by init (after checking force_reload, etc)
    # try:
    dataset = SpatialRNA(
        root="data/test_sample/",
        sample_name="test_sample",
        radius_r=15,
        tile_by_dim="y",
        dim_x="x",
        dim_y="y",
        num_tiles=2,
        load_type="subgraph",
        load_tile_id=0,
        process_tile_ids=[1],
        process_mode="subgraph",
        subgraph_mode="link_based",
        num_sampled_edges=2,
        num_neighbors = [-1,-1],
        batch_size = 4,
        neg_sampling = NegativeSampling(mode="triplet",amount=1),
        one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
        log=True
    )
    assert dataset[0] is None
    # except Exception as e:
    #     assert isinstance(e, TypeError)
    dataset = SpatialRNA(
            root="data/test_sample/",
            sample_name="test_sample",
            radius_r=11,
            tile_by_dim="y",
            dim_x="x",
            dim_y="y",
            num_tiles=2,
            load_type="subgraph",
            load_tile_id=1,
            process_tile_ids=[0],
            process_mode="subgraph",
            subgraph_mode="link_based",
            num_sampled_edges=2,
            num_neighbors = [-1,-1],
            batch_size = 4,
            neg_sampling = NegativeSampling(mode="triplet",amount=1),
            one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
            log=True
        )
    clean_test_data()
    create_test_data()
    dataset = SpatialRNA(
            root="data/test_sample/",
            sample_name="test_sample",
            radius_r=11,
            tile_by_dim="y",
            dim_x="x",
            dim_y="y",
            num_tiles=2,
            load_type="subgraph",
            load_tile_id=0,
            process_tile_ids=[0],
            process_mode="subgraph",
            subgraph_mode="link_based",
            num_sampled_edges=2,
            num_neighbors = [-1,-1],
            batch_size = 4,
            neg_sampling = NegativeSampling(mode="triplet",amount=1),
            one_hot_encoding={"gene1": 0, "gene2": 1, "gene3": 3},
            log=False
    )

    #clean_test_data()


