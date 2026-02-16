import numpy as np
from scipy.optimize import curve_fit

def pol0(x,b):
    return b - x


def pol1(x, b, a):
    return a * x + b


def gauss(x, A, mu, sigma): 
    return A * np.exp(-((x - mu) / sigma)**2 / 2)


def fit_function(data, func, valid_range=None, p0=None, bounds=None, debug=False):
    """
    任意の関数でデータをフィットする汎用関数。

    Parameters
    ----------
    data : list or array-like
        フィットデータ。data[0] が x データ、data[1] が y データのリストまたは配列。
    func : callable
        フィットする関数（例: gauss）。関数のシグネチャは func(x, *params) であること。
    valid_range : tuple, optional
        フィット範囲 (xmin, xmax)。None の場合、全範囲を使用。
    p0 : list, optional
        初期パラメータ値のリスト。None の場合、デフォルト値を推定。
    bounds : list of tuples, optional
        パラメータの境界 [(min, max), (min, max), ...]。None の場合、デフォルト境界を使用。
    debug : bool, optional
        True の場合、デバッグ情報を出力。デフォルトは False。  

    Returns
    -------
    popt : array
        最適パラメータ。    
    
    perr : array    
        パラメータの誤差。
    """
    x = np.asarray(data[0], dtype=float)
    y = np.asarray(data[1], dtype=float)

    if valid_range is not None:
        xmin, xmax = valid_range
        mask = (x >= xmin) & (x <= xmax) & np.isfinite(x) & np.isfinite(y)
        x_fit = x[mask]
        y_fit = y[mask]
    else:
        mask = np.isfinite(x) & np.isfinite(y)
        x_fit = x[mask]
        y_fit = y[mask]
        xmin = float(np.min(x_fit))
        xmax = float(np.max(x_fit))

    if x_fit.size < 4:
        raise ValueError(f"Too few points in fit range: {x_fit.size}")

    import inspect
    sig = inspect.signature(func)
    num_params = len(sig.parameters) - 1  # x を除いたパラメータ数
    if num_params < 1:
        raise ValueError("Function must have at least one parameter besides x.")

    # 初期値の設定
    if p0 is None:
        p0 = [0.1] * num_params
        
    elif len(p0) != num_params:
        raise ValueError(f"p0 length {len(p0)} does not match function parameters {num_params}.")

    # 境界の設定
    if bounds is None:
        bounds = ([-np.inf] * num_params, [np.inf] * num_params)

    else:
        bounds = tuple(map(list, zip(*bounds)))
        if len(bounds[0]) != num_params or len(bounds[1]) != num_params:
            raise ValueError(f"bounds length does not match function parameters {num_params}.")

    if debug:
        print("Function:", func.__name__)
        print("p0:", p0)
        print("bounds:", bounds)

    popt, pcov = curve_fit(func, x_fit, y_fit, p0=p0, bounds=bounds, maxfev=20000)
    perr = np.sqrt(np.diag(pcov))

    if debug:
        print("Fitted parameters:", popt)
        print("Parameter errors:", perr)

    return popt, perr