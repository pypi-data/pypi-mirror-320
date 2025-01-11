import numpy as np

def aggregate_cells(X_ann_sample, label, name, layer=None):
    if layer is not None:
        pseudobulk = X_ann_sample.layers[layer].sum(axis=0)
    else:
        pseudobulk = X_ann_sample.X.sum(axis=0)
    obs = X_ann_sample.obs.loc[[name]].drop_duplicates()
    obs.index = [label]
    pseudobulk_ann = sc.AnnData(X=pd.DataFrame(pseudobulk),
                                var=X_ann_sample.var,
                                obs=obs)
    return pseudobulk_ann

def pseudo_bulk_KNN(X_ann,
                    class_col,
                    nb_pseudo_replicates=100,
                    random_state=33,
                    nb_cells_per_pseudobulk=50,
                    layer=None,
                    ):
    np.random.seed(random_state)
    pseudobulks = []
    sc.pp.neighbors(X_ann, n_neighbors=nb_cells_per_pseudobulk)
    cell_name_index = {name:i for i,name in enumerate(X_ann.obs.index)}
    connectivity = X_ann.obsp['connectivities']
    counter = 0
    for cell_type in tqdm(X_ann.obs[class_col].unique(), leave=True, position=0, desc=class_col):
        cell_type_subset=X_ann[X_ann.obs[class_col]==cell_type,:]
        sampled_seed_cells = np.random.choice(cell_type_subset.obs.index,
                                              size=nb_pseudo_replicates,
                                              replace=True)
        
        for name in tqdm(sampled_seed_cells,leave=False, position=1):
            i = cell_name_index[name]
            mask = (connectivity[i,:]!=0)[0].todok()
            mask[0,i] = True
            X_ann_sample = X_ann[mask]
            label = f"{cell_type}-{name}-{counter}"
            pseudobulk = aggregate_cells(X_ann_sample, label, name, layer)
            pseudobulks.append(pseudobulk)
            counter += 1
    pseudobulk = sc.concat(pseudobulks)
    pseudobulk.var = X_ann.var
    return pseudobulk


def pseudo_bulk_random(X_ann,
                        class_col,
                        nb_pseudo_replicates=10,
                        random_state=33,
                        nb_cells_per_pseudobulk=10,
                        ):
    np.random.seed(random_state)
    pseudobulks = []
    for cell_type in tqdm(X_ann.obs[class_col].unique(), leave=True, position=0, desc=class_col):
        cell_type_subset=X_ann[X_ann.obs[class_col]==cell_type,:]
        for i in tqdm(range(nb_pseudo_replicates),leave=False, position=1): 
            sampled_indices = np.random.choice(list(cell_type_subset.obs.index),
                                                size=nb_cells_per_pseudobulk,
                                                replace=True)
            label = f"{cell_type}-{i}"
            X_ann_sample = cell_type_subset[sampled_indices]
            pseudobulk = aggregate_cells(X_ann_sample, label,sampled_indices[0])
            pseudobulks.append(pseudobulk)
    pseudobulk = sc.concat(pseudobulks)
    pseudobulk.var = X_ann.var
    return pseudobulk
