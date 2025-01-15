"""specific test for the jp2kvolume. the large part is in test_single_frame_volume as most of the processing is common"""

import os
import numpy

from tomoscan.esrf.volume.jp2kvolume import JP2KVolume
from tomoscan.esrf.volume.mock import create_volume

_data = create_volume(
    frame_dims=(100, 100), z_size=11
)  # z_size need to be at least 10 to check loading from file name works
for i in range(len(_data)):
    _data[i] += 1
_data = _data.astype(numpy.uint16)


def test_jp2kvolume_rescale(tmp_path):
    """
    Test that rescale is correctly applied by default by the JP2KVolume
    """
    acquisition_dir = tmp_path / "acquisition"
    os.makedirs(acquisition_dir)
    volume_dir = str(acquisition_dir / "volume")
    os.makedirs(volume_dir)
    volume = JP2KVolume(folder=volume_dir, data=_data, metadata={})
    volume.save()

    volume.clear_cache()
    volume.load()
    assert volume.data.min() == 0
    assert volume.data.max() == numpy.iinfo(numpy.uint16).max
