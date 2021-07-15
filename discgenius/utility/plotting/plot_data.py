import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import os
from PIL import Image
import pylab
import sys
import glob

ROOT_DIR = os.path.abspath(os.curdir)


def image_trim(image_name):
    im = Image.open(image_name)
    im2 = im.crop(im.getbbox())
    im2.save(image_name)


# extends list to given resolution by expanding based on input/target ratio
# each datapoint is either linearly interpolated to the next datapoint or repeated
#
def extend_list(data, target_resolution, midpoint, interpolate=True, cut_offset=0):
    """
    extends list to given resolution by expanding based on input/target ratio

    :param data: input list
    :param target_resolution: target resolution of input list
    :param midpoint: target midpoint within resolution
    :param interpolate: controls whether each datapoint is either linearly interpolated to the next datapoint or repeated
    :param cut_offset: controls volume cut off for midpoint
    :return:
    """
    ratio = int(np.floor((target_resolution - cut_offset) / len(data)))
    offset_ratio = int(np.floor(target_resolution / len(data)))
    offset = target_resolution - (offset_ratio * len(data))
    print(ratio, offset_ratio, offset)
    result = []
    result.extend(np.full(int(np.floor(offset / 2)), data[0]))
    cut_performed = False
    for i, d in enumerate(data[:-1]):
        # data for entire width
        if interpolate:
            data_prep = np.linspace(d, data[i + 1], (ratio + 1))
        else:
            data_prep = np.full((ratio + 1), d)
        # perform cut at or before midpoint
        if cut_offset > 0 and (len(result) + ratio) > midpoint and not cut_performed:
            distance_to_midpoint = (-midpoint + len(result)) * -1
            result.extend(np.full(distance_to_midpoint, result[-1]))
            result.extend(np.full(cut_offset, 0))
            if interpolate:
                result.extend(data_prep[distance_to_midpoint:-1])
            else:
                result.extend(np.full((ratio - distance_to_midpoint), data[i + 1]))
            cut_performed = True
        else:
            result.extend(data_prep[:-1])
    result.extend(np.full((ratio + int(np.ceil(offset / 2))), data[-1]))
    return result


def plot_eq(plot_name, target_path, song_a_highs, song_a_mids, song_a_lows, song_b_highs, song_b_mids, song_b_lows,
            transition_length=64,
            transition_midpoint=32,
            margin=0.1,
            bass_cut=True,
            legend=False):
    plot_data = []
    song_a_data = {
        'highs': extend_list(song_a_highs, transition_length, transition_midpoint),
        'mids': extend_list(song_a_mids, transition_length, transition_midpoint)
    }
    song_b_data = {
        'highs': extend_list(song_b_highs, transition_length, transition_midpoint),
        'mids': extend_list(song_b_mids, transition_length, transition_midpoint)
    }
    if bass_cut:
        song_a_data['lows'] = extend_list(song_a_lows,
                                          transition_length, transition_midpoint,
                                          interpolate=False, cut_offset=8)
        song_b_data['lows'] = extend_list(song_b_lows, transition_length, transition_midpoint, interpolate=False,
                                          cut_offset=8)
    else:
        song_a_data['lows'] = extend_list(song_a_lows, transition_length, transition_midpoint, interpolate=False)
        song_b_data['lows'] = extend_list(song_b_lows, transition_length, transition_midpoint, interpolate=False)

    plot_y = range(0, transition_length)
    plot_data.append({
        'x': np.full(transition_length, 0.0),
        'y': plot_y,
        'z': song_a_data['highs']
    })
    plot_data.append({
        'x': np.full(transition_length, 0.1),
        'y': plot_y,
        'z': song_a_data['mids']
    })
    plot_data.append({
        'x': np.full(transition_length, 0.2),
        'y': plot_y,
        'z': song_a_data['lows']
    })
    plot_data.append({
        'x': np.full(transition_length, 0.3),
        'y': plot_y,
        'z': song_b_data['highs']
    })
    plot_data.append({
        'x': np.full(transition_length, 0.4),
        'y': plot_y,
        'z': song_b_data['mids']
    })
    plot_data.append({
        'x': np.full(transition_length, 0.5),
        'y': plot_y,
        'z': song_b_data['lows']
    })

    # plot prepared data
    colors = ["#76B900", "#b0a300", "#e18300", "#0082d1", "#b565cd", "#2F4858"]

    fig, ax = plt.subplots(subplot_kw={'projection': '3d'}, figsize=(10, 8))
    for index, data in enumerate(plot_data):
        data_bounds = ({
            "x": [(margin * index), (margin * index)],
            "y": [data["y"][0], data["y"][-1]],
            "z": [data["z"][0], data["z"][-1]]})
        ax.plot(data["x"], data["y"], data["z"], color=colors[index], linewidth=5)
        ax.scatter(data_bounds["x"], data_bounds["y"], data_bounds["z"], color=colors[index], s=100)
    ax.plot([0, 0], [0, 0], [0, 1], color="gray", linestyle=":")
    ax.plot([0, 0], [transition_length, transition_length], [0, 1], color="gray", linestyle=":")

    ax.set_box_aspect((2, 5, 2))
    ax.view_init(15, 5)
    plt.axis('off')
    plt.xlim(0, 1)
    if legend:
        labels = ["Song 1 Highs", "Song 1 Mids", "Song 1 Lows",
                  "Song 2 Highs", "Song 2 Mids", "Song 2 Lows"]
        plt.legend(labels=labels,
                   bbox_to_anchor=(1.05, 1),
                   loc='upper left',
                   markerscale=20.0,
                   prop={
                       'size': 20
                   })
    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                        hspace=0, wspace=0)
    plt.margins(0, 0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig(plot_name, transparent=True, bbox_inches='tight')
    plot_with_extension = f"{plot_name}.png"
    print(f"Saved plot image to {target_path}/{plot_with_extension}")
    return plot_with_extension


if __name__ == "__main__":
    # _song_a_highs = [1, 0.8, 0.7, 0.6, 0.5, 0]
    # _song_a_mids = [1, 0.8, 0.7, 0.6, 0.5, 0]
    # _song_a_lows = [1, 1, 0, 0]
    # _song_b_highs = [0, 0.5, 0.6, 0.7, 0.8, 1]
    # _song_b_mids = [0, 0.5, 0.6, 0.7, 0.8, 1]
    # _song_b_lows = [0, 0, 1, 1]
    # _plot_name = "VFF"
    # plot_filename = plot_eq(_plot_name, ROOT_DIR,
    #                         _song_a_highs, _song_a_mids, _song_a_lows,
    #                         _song_b_highs, _song_b_mids, _song_b_lows,
    #                         margin=0.1, bass_cut=False)
    # image_trim(plot_filename)
    # _plot_name = "VFF_cut"
    # plot_filename = plot_eq(_plot_name, ROOT_DIR,
    #                         _song_a_highs, _song_a_mids, _song_a_lows,
    #                         _song_b_highs, _song_b_mids, _song_b_lows,
    #                         margin=0.1, bass_cut=True)
    # image_trim(plot_filename)

    _eqgf_a_norm = [(1 + (x / 20)) for x in [0, -0.5, -1, -1.7, -2.8, -3.8, -5.5, -7.5, -9.5, -20]]
    _eqgf_b_norm = [(1 + (x / 20)) for x in [-20, -20, -16, -10, -7.5, -6, -4.5, -2.8, -1.2, 0]]

    _song_a_highs = _eqgf_a_norm
    _song_a_mids = _eqgf_a_norm
    _song_a_lows = [1, 1, 0, 0]
    _song_b_highs = _eqgf_b_norm
    _song_b_mids = _eqgf_b_norm
    _song_b_lows = [0, 0, 1, 1]
    # _plot_name = "EQ"
    # plot_filename = plot_eq(_plot_name, ROOT_DIR,
    #                         _song_a_highs, _song_a_mids, _song_a_lows,
    #                         _song_b_highs, _song_b_mids, _song_b_lows,
    #                         margin=0.1, bass_cut=False)
    # image_trim(plot_filename)
    #
    # _plot_name = "EQ_cut"
    # plot_filename = plot_eq(_plot_name, ROOT_DIR,
    #                         _song_a_highs, _song_a_mids, _song_a_lows,
    #                         _song_b_highs, _song_b_mids, _song_b_lows,
    #                         margin=0.1, bass_cut=True)
    # image_trim(plot_filename)

    _plot_name = "EQ_cut_legend"
    plot_filename = plot_eq(_plot_name, ROOT_DIR,
                            _song_a_highs, _song_a_mids, _song_a_lows,
                            _song_b_highs, _song_b_mids, _song_b_lows,
                            margin=0.1, bass_cut=True, legend=True)
    image_trim(plot_filename)
