"""تفريغ الدرس الثاني جملةً جملة: تُقطع الأجزاء عند سكتات الشيخ، فيكون لكل جزء وقت بدايته بالضبط."""
import sherpa_onnx, numpy as np, wave, json, glob, sys
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
M = f'{S}/asr/sherpa-onnx-whisper-small'
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f'{M}/small-encoder.int8.onnx', decoder=f'{M}/small-decoder.int8.onnx',
                                                 tokens=f'{M}/small-tokens.txt', language='ar', task='transcribe', num_threads=4)
w = wave.open(f'{S}/asr/l2_16k.wav'); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
P = np.load(f'{S}/l2/pauses.npy')
T0, T1 = float(sys.argv[1]), float(sys.argv[2])
cuts = [b for a, b in P if T0 < b < T1]            # بدايات الكلام بعد كل سكتة
bounds = [T0] + cuts + [T1]
segs = []
for a, b in zip(bounds[:-1], bounds[1:]):
    # نهاية الجزء: بداية السكتة التالية
    nxt = [pa for pa, pb in P if a < pa <= b]
    e = nxt[-1] if nxt else b
    if segs and (segs[-1][1] - segs[-1][0] < 2.0):  # جزء قصير جداً يُضم إلى ما بعده
        segs[-1] = (segs[-1][0], e)
    else:
        segs.append((a, e))
out = []
for a, e in segs:
    s = rec.create_stream(); s.accept_waveform(16000, x[int(a * 16000):int(e * 16000)]); rec.decode_stream(s)
    out.append(dict(start=round(a, 2), end=round(e, 2), text=s.result.text.strip()))
    print(f'{int(a // 60)}:{a % 60:05.2f}  {s.result.text.strip()}', flush=True)
json.dump(out, open(f'{S}/asr/transcript_{int(T0)}_{int(T1)}.json', 'w'), ensure_ascii=False, indent=0)
