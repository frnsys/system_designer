import numpy as np
from brood.agent import State


# from: <https://aiomas.readthedocs.io/en/latest/guides/codecs.html>
def get_np_serializer():
   """Return a tuple *(type, serialize(), deserialize())* for NumPy arrays
   for usage with an :class:`aiomas.codecs.MsgPack` codec."""
   return np.ndarray, _serialize_ndarray, _deserialize_ndarray


def _serialize_ndarray(obj):
   return {
      'type': obj.dtype.str,
      'shape': obj.shape,
      'data': obj.tostring(),
   }


def _deserialize_ndarray(obj):
   array = np.fromstring(obj['data'], dtype=np.dtype(obj['type']))
   return array.reshape(obj['shape'])


def get_state_serializer():
    return State, _serialize_state, _deserialize_state


def _serialize_state(obj):
    return obj.__dict__


def _deserialize_state(obj):
    return State(**obj)
