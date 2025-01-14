import pytest
import torch

from audiozen.loss import BinauralLoss


@pytest.fixture
def binaural_loss():
    return BinauralLoss(n_fft=512, win_length=400, hop_length=160, sr=16000)


def test_forward_snr_loss(binaural_loss):
    est = torch.rand(2, 2, 16000)
    ref = torch.rand(2, 2, 16000)
    binaural_loss.snr_loss_weight = 1.0
    binaural_loss.stoi_weight = 0.0
    binaural_loss.ild_weight = 0.0
    binaural_loss.ipd_weight = 0.0

    loss = binaural_loss(est, ref)
    assert isinstance(loss, torch.Tensor)
    assert isinstance(loss.item(), float)


def test_forward_stoi_loss(binaural_loss):
    est = torch.rand(2, 2, 16000)
    ref = torch.rand(2, 2, 16000)
    binaural_loss.snr_loss_weight = 0.0
    binaural_loss.stoi_weight = 1.0
    binaural_loss.ild_weight = 0.0
    binaural_loss.ipd_weight = 0.0

    loss = binaural_loss(est, ref)
    assert isinstance(loss, torch.Tensor)
    assert loss.item() > 0


def test_forward_ild_loss(binaural_loss):
    est = torch.rand(2, 2, 16000)
    ref = torch.rand(2, 2, 16000)
    binaural_loss.snr_loss_weight = 0.0
    binaural_loss.stoi_weight = 0.0
    binaural_loss.ild_weight = 1.0
    binaural_loss.ipd_weight = 0.0

    loss = binaural_loss(est, ref)
    assert isinstance(loss, torch.Tensor)
    assert loss.item() > 0


def test_forward_ipd_loss(binaural_loss):
    est = torch.rand(2, 2, 16000)
    ref = torch.rand(2, 2, 16000)
    binaural_loss.snr_loss_weight = 0.0
    binaural_loss.stoi_weight = 0.0
    binaural_loss.ild_weight = 0.0
    binaural_loss.ipd_weight = 1.0

    loss = binaural_loss(est, ref)
    assert isinstance(loss, torch.Tensor)
    assert loss.item() > 0


def test_forward_combined_loss(binaural_loss):
    est = torch.rand(2, 2, 16000)
    ref = torch.rand(2, 2, 16000)
    binaural_loss.snr_loss_weight = 0.1
    binaural_loss.stoi_weight = 0.1
    binaural_loss.ild_weight = 0.1
    binaural_loss.ipd_weight = 0.1

    loss = binaural_loss(est, ref)
    assert isinstance(loss, torch.Tensor)
    assert loss.item() > 0
