from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr


def calculate_correlation(x, y, nodes):
    """
    Filters a given dataset, then finds Pearson correlation between first principal component of filtered dataset and
    target variable.

    :param x: Full, unfiltered dataset, as a pandas DataFrame.
    :param y: Target variable.
    :param nodes: Indices of columns in full dataset to consider.
    :return: (correlation, p-value)
    """
    filt_x = x.iloc[:, nodes]

    scaler = StandardScaler()
    scaled_x = scaler.fit_transform(filt_x)

    pca = PCA(n_components=1)
    pc1 = [i for i, in pca.fit_transform(scaled_x)]

    y_col = y.iloc[:, 0]

    corr, p_val = pearsonr(pc1, y_col)
    var_ex = pca.explained_variance_ratio_[0]

    return corr, p_val, var_ex
