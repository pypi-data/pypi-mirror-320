from torch_geometric.data import InMemoryDataset, Dataset, Data
from typing import Callable, Optional, List
from torch_geometric.nn import radius_graph
import os
import os.path as osp
import pandas as pd
import torch
from torch_geometric.io import fs
from torch_geometric.loader import LinkNeighborLoader



## feature matrix. Reduce mem and I/O by mapping gene label to int IDs. Delay mapping to 1-D tensors when training.
## TODO: warnings about different num_tiles, radius_r arguments if only loading not processing
    
def files_exist(files: List[str]) -> bool:
    # NOTE: We return `False` in case `files` is empty, leading to a
    # re-processing of files on every instantiation.
    return len(files) != 0 and all([fs.exists(f) for f in files])

class SpatialRNA(InMemoryDataset):
    r"""A spatial RNA graph dataset. One dataset per tissue sample, and optionally creates 
    tiles from a tissue area. For each generated data.pt, it contains the nodes in core areas for
    making inference for transcripts with complete neighbourhoods.


    Args:
        root (str): Root directory where the dataset should be saved.
        sample_name (str): The name of this sample. Appended to the processed [sample_name]_data.pt. 
                           Using basename of root dir if not supplied.
        radius_r (float): The radius for building RNA graphs.
        tile_by_dim (str): Along which dimension to make tiles. It should be a column in the transcript data.frame. 
        num_tiles (int): The number of tiles to create from this tissue sample.
        process_mode (str): The mode of process can be either "tile" or "subgraph".
        load_type (str): If :obj:`"tile"`, load the tile graph data. 
            If :obj:`"subgraph"`, load the tile subgraph data. 
        load_tile_id (int): Select one tile to load.
        process_tile_ids (List[int]): Select tiles to process including generating tile graph and subgraph.
        one_hot_encoding (dict): Dictionary that mapps gene names to integer (or one-hot-encoding tensors). 
            It is essential to apply the same dictionary for all samples that are analyzed together.
        transform (callable, optional): A function/transform that takes in an
            :obj:`torch_geometric.data.Data` object and returns a transformed
            version. The data object will be transformed before every access.
            (default: :obj:`None`)
        pre_transform (callable, optional): A function/transform that takes in
            an :obj:`torch_geometric.data.Data` object and returns a
            transformed version. The data object will be transformed before
            being saved to disk. (default: :obj:`None`)
        force_reload (bool, optional): Whether to re-process the dataset.
            (default: :obj:`False`)
        force_resample (bool, optional): Whether to re-process the tile dataset to generate subgraphs.
            (default: :obj:`False`)
        subgraph_mode (str): The mode of subgraph generation can be either "link_based" or "node_based".
            (default: :obj:`link_based`)   
        num_sampled_edges (int): sample this many edge_index as positive edges when generating subgraph from a tile (used in LinkNeighborLoader).
        num_seed_nodes:(int, optional): Number of seed nodes for generating subgraphs.
            (default: :obj:`5000`)   
        num_walks:(int, optional): Number of walks for generating subgraphs.
            (default: :obj:`5`) 
    
        log (bool, optional): Whether to print any console output while
            downloading and processing the dataset. (default: :obj:`True`)
        **kwargs (optional): Additional arguments of
            :class:`torch.utils.data.LinkNeighborLoader`, such as :obj:`num_neighbors`
    """
    def __init__(
        self, 
        root: str, 
        sample_name: Optional[str] = None,
        radius_r: float = 3.0,
        dim_x: str = "X",
        dim_y: str = "Y",
        tile_by_dim: str = "Y",
        num_tiles: int = 1,
        process_mode: str = "tile",
        load_type: str = "tile",
        load_tile_id: int = 0,
        pad_hops: float = 2,
        feature_col = "gene",
        max_num_neighbors: int = 500,
        process_tile_ids: List[int] = None,
        one_hot_encoding: dict = None,
        subgraph_mode: str = "link_based",
        num_sampled_edges: int = 5000,
        num_seed_nodes: int = 5000,
        num_walks: int = 5,
        transform = None, 
        pre_transform = None,
        force_reload: bool = False,
        force_resample: bool = False,
        log: bool= True,
        seed: int = 100,
        **kwargs,

    )-> None:
        assert load_type in ["tile","subgraph","blank"]
        assert process_mode in ["tile", "subgraph"]
        assert subgraph_mode in ["link_based", "node_based"]

        self.num_tiles = num_tiles
        if sample_name is not None:
            self.sample_name = sample_name
        else:
            self.sample_name = osp.basename(root)

        self.radius_r = radius_r
        self.load_tile_id = load_tile_id
        self.pad_hops = pad_hops
        self.max_num_neighbors = max_num_neighbors
        self.one_hot_encoding = one_hot_encoding
        self.seed = seed
        self.feature_col = feature_col
        self.num_sampled_edges = num_sampled_edges
        self.load_type = load_type
        self.process_mode = process_mode
        self.num_seed_nodes = num_seed_nodes
        self.num_walks = num_walks
        
        assert tile_by_dim in [dim_x,dim_y]
        assert one_hot_encoding is not None
        
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.tile_by_dim = tile_by_dim
        self.log = log
        self.force_resample = force_resample
        self.subgraph_mode = subgraph_mode

        if process_tile_ids is None:
            self.process_tile_ids = [load_tile_id]
        else:
            self.process_tile_ids = process_tile_ids
        # super init, process tiles, if tiles.pt not exist, and regenerate if force_reload=True.
        super().__init__(root, transform, pre_transform,force_reload=force_reload, log=log)
        # subsequently generates the subgraphs if requested
        if process_mode == "subgraph":
            self.generate_subgraph(**kwargs)

        if load_type == 'subgraph':
            load_file_name = osp.join(self.subgraph_dir,f'{self.sample_name}_subgraph_data_tile{self.load_tile_id}.pt')
            # if self.force_resample or not files_exist([load_file_name]):
            #     self.generate_subgraph(**kwargs)
        elif load_type == 'tile':
            load_file_name = osp.join(self.processed_dir,f'{self.sample_name}_data_tile{self.load_tile_id}.pt')
        else:
            load_file_name = None

        if load_file_name is None:
            print(load_file_name," not exist, nothing loaded")
        elif files_exist([load_file_name]):
            print("loading from file ",load_file_name)
            self.load(load_file_name)
        else:
            print(load_file_name," not exist, nothing loaded")
        None
        

    @property
    def subgraph_dir(self) -> str:
        return osp.join(self.root,"subgraph")

    @property
    def raw_file_names(self):
        return [f'{self.sample_name}.csv']

    @property
    def subgraph_file_names(self):
        return [f'{self.sample_name}_subgraph_data_tile{tile}.pt' for tile in self.process_tile_ids]

    @property
    def processed_file_names(self):
        return [f'{self.sample_name}_data_tile{tile}.pt' for tile in self.process_tile_ids]

    @property
    def subgraph_paths(self) -> List[str]:
        r"""The absolute filepaths for generated subgraph data from each sample tile
        """
        files = self.subgraph_file_names
        # Prevent a common source of error in which `file_names` are not
        # defined as a property.
        if isinstance(files, Callable):
            files = files()
        return [osp.join(self.subgraph_dir, f) for f in list(files)]
        
    def get_padding(self, log:bool, tile_df, full_df, padding:float):
        r"""A helper function to get the padding area for a tile of tissue. 
            Args:
                log (bool), whether to print logs
                tile_df: the data.frame with current tile.
                full_df: original tissue data.frame
                padding: size of the padding (used for padding the core area of the tile)
        """
        left_most = tile_df[self.tile_by_dim].min()
        right_most = tile_df[self.tile_by_dim].max()

        padding_left_mask = (full_df[self.tile_by_dim] >= (left_most - padding)) & (full_df[self.tile_by_dim] < left_most)
        padding_right_mask = (full_df[self.tile_by_dim] > (right_most)) & (full_df[self.tile_by_dim] <=  (right_most + padding))

        if log:
            print("left padding shape ",padding_left_mask.sum())
            print("right padding shape ",padding_right_mask.sum())

        padding_left_df = full_df[padding_left_mask]
        padding_right_df = full_df[padding_right_mask]

        padding_left_df = padding_left_df.assign(core_mask = False)
        padding_right_df = padding_right_df.assign(core_mask = False)

        return pd.concat([padding_left_df,padding_right_df])


    def generate_subgraph(self,**kwargs):
        import random 
        import sys
        if self.log:
            print("To generate subgraphs for ",self.subgraph_paths)

        if files_exist(self.subgraph_paths) and not self.force_resample:
            print("Subgraphs already exist, skipping subgraph generation")
            return
        elif not files_exist(self.processed_paths):
            sys.exit("Wrong logic in generate_subgraph function. Attempted to generate subgraphs when tile graphs are not available")

        for s_id in self.process_tile_ids:
            random.seed(self.seed)
            if self.log:
                print("Loading processed data tile for subgraphing ", osp.join(self.processed_dir,f'{self.sample_name}_data_tile{s_id}.pt'))

            tile_data = torch.load(osp.join(self.processed_dir,f'{self.sample_name}_data_tile{s_id}.pt'),weights_only=True)
            print("load tile data from ", osp.join(self.processed_dir,f'{self.sample_name}_data_tile{s_id}.pt'))
            tile_data = Data(**tile_data[0])
            print(tile_data)

            if self.subgraph_mode == "link_based":
                if self.log:
                    print("Generating subgraphs for tile ", s_id, "Sampling " ,self.num_sampled_edges, " edges") 
                sampled_edge_index = tile_data.edge_index[:,random.sample(range(tile_data.edge_index.shape[1]),self.num_sampled_edges)]

                subgraph_loader = LinkNeighborLoader(
                    data = tile_data,
                    edge_label_index = sampled_edge_index,
                    **kwargs
                )
                # subgraph_g = []
                # ## Get one batch as the sampled subgraph from the tissue tile
                # for batch in subgraph_loader:
                #     subgraph_g = subgraph_g + [batch]
                #     break
            elif self.subgraph_mode == "node_based":
                if self.log:
                    print("Generating subgraphs for tile ", s_id, "Sampling ", self.num_seed_nodes, " nodes with ", self.num_walks, " random walks.")
                random.seed(self.seed)
                sample_nodes = random.sample(range(tile_data.x.squeeze().size()[0]),self.num_seed_nodes)
                sample_nodes_bywalks = torch.tensor(sample_nodes * self.num_walks)
                sample_nodes_bywalks = sample_nodes_bywalks.sort().values
                from torch_cluster import random_walk
                sampled_edges_by_random_walk = random_walk(
                    row = tile_data.edge_index[0],
                    col = tile_data.edge_index[1], 
                    start = sample_nodes_bywalks, 
                    walk_length = 1, # 1 to get immediate neighbours
                    return_edge_indices=False
                ) 

                if self.log:
                    print("batch size ", sampled_edges_by_random_walk.squeeze().size()[0])
                    print("start node  ", sample_nodes_bywalks, "size " , sample_nodes_bywalks.size())
                    print(" sampled_edges_by_random_walk ", sampled_edges_by_random_walk)

                subgraph_loader  = LinkNeighborLoader(
                    data = tile_data,
                    batch_size = sampled_edges_by_random_walk.squeeze().size()[0],
                    edge_label_index = torch.stack(
                        [sampled_edges_by_random_walk[:,0],sampled_edges_by_random_walk[:,1]]
                    ),   
                    **kwargs
                )   
            subgraph_g = []
            ## Get one batch as the sampled subgraph from the tissue tile
            for batch in subgraph_loader:
                subgraph_g = subgraph_g + [batch]
                break
            ## simplify g before saving
            subgraph_g = Data(x = subgraph_g[0].x, edge_index = subgraph_g[0].edge_index, edge_label_index = subgraph_g[0].edge_label_index)
            self.save([subgraph_g], osp.join(self.subgraph_dir,f'{self.sample_name}_subgraph_data_tile{s_id}.pt'))
    def process(self)-> None:
        # Load raw data
        import numpy as np
        if self.log:
            print("Processing raw file ",self.raw_paths[0])
            print("To create processed files ", self.processed_paths)

        raw_data = pd.read_csv(self.raw_paths[0])
        if self.log:
            print(f'Raw data shape {raw_data.shape[0]}')

        raw_data["trans_id"] = np.arange(raw_data.shape[0])
        ## cutting along one selected axis 
        raw_data["tiles_range"] = pd.cut(
            raw_data[self.tile_by_dim],
            bins = self.num_tiles, 
            labels= ["tile"+str(x) for x in range(self.num_tiles)]
        )

        for tile in self.process_tile_ids:
            tile_df = raw_data[raw_data.tiles_range == ("tile"+str(tile))]
            if self.log:
                print("tile core area shape ", tile_df.shape)
            assert tile_df.shape[0] > 0, "The requested tile contains no transcripts, likely due to the tile id is not in the range 0:(num_tiles-1)"
            tile_df = tile_df.assign(core_mask=True)
            padding_df = self.get_padding(
                log = self.log, 
                tile_df = tile_df, 
                full_df = raw_data, 
                padding = self.pad_hops * self.radius_r
            )
            tile_df = pd.concat([tile_df,padding_df])
            if self.log:
                print("core area plus paddings, shape ", tile_df.shape)
            
            if isinstance(next(iter(self.one_hot_encoding.items()))[1],int):
                feature_x = torch.tensor([self.one_hot_encoding[x] for x in tile_df[self.feature_col]])
            else:
                feature_x = torch.stack([self.one_hot_encoding[x] for x in tile_df[self.feature_col]])
            xy_pos = torch.tensor(np.array(tile_df[[ self.dim_x , self.dim_y]]))

            edge_index = radius_graph(xy_pos, r = self.radius_r, max_num_neighbors = self.max_num_neighbors)

            data_1 = Data(
                x = feature_x, 
                edge_index = edge_index, 
                trans_id = torch.tensor(list(tile_df.trans_id)),
                core_mask = torch.tensor(list(tile_df.core_mask)))

            self.save([data_1], osp.join(self.processed_dir,f'{self.sample_name}_data_tile{tile}.pt'))
