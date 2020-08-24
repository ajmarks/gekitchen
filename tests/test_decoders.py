"""Test ERD value decoders and encoders."""
from gekitchen import erd_utils
from gekitchen.erd_utils import (
    decode_signed_byte, encode_signed_byte
)


def test_signed_byte():
    for i in range(-127, 129):
        assert decode_signed_byte(encode_signed_byte(i)) == i


def test_decoder_args():
    """Test that all encoders are typed to take a single string"""
    decoders = [getattr(erd_utils, x) for x in dir(erd_utils) if "decode_" in x]
    for dec in decoders:
        annotations = dec.__annotations__
        assert len(annotations) == 2
        assert annotations['value'] is str


def test_encoder_return():
    """Test that all encoders are typed to give the correct return value"""
    encoders = [getattr(erd_utils, x) for x in dir(erd_utils) if "encode_" in x]
    for enc in encoders:
        annotations = enc.__annotations__
        assert len(annotations) == 2
        assert annotations['return'] is str
