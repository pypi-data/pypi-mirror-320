import synthesistoolkit as stk

def test_samplerate():
    sr = 41919
    stk.set_sample_rate(sr)
    assert stk.sample_rate() == sr