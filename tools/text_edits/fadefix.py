"""مقطع معاد رسمه، وإطارات انتقاله الأخيرة تُبنى بمنحنى انتقال الأصل نفسه:
لكل إطار من الأصل: c = نسبة بقاء المحتوى، k = عامل الإعتام؛ والإطار الجديد = (اللوح + c·(الحالة الجديدة − اللوح))·k."""
import sys, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/regroup')
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/splice')
import partial as PT, splice as SP
PL = PT.R.PLATE


def curve(video, t_pre, t_end):
    """(n, c, k) لإطارات الأصل من t_pre إلى t_end، مقيسة على الحالة عند t_pre."""
    import sched as SC
    S0 = None; out = []
    for i, f in enumerate(SC.stream(video, t_pre, t_end + 0.05)):
        ff = f.astype(np.float32)
        if S0 is None:
            S0 = ff; d = S0 - PL
            flat = np.abs(d).max(2) < 4; strong = np.abs(d).max(2) > 40
            dd = d[strong]
        k = float(np.median((ff[flat] / np.maximum(PL[flat], 1)).ravel()))
        x = ff[strong] / k - PL[strong]
        c = float(np.clip((x * dd).sum() / (dd * dd).sum(), 0, 1))
        out.append((int(round(t_pre * 30)) + i, c, k))
    return out


class FadedClip(SP.Clip):
    """قبل الانتقال: إطارات المقطع المعاد رسمه. أثناءه: يُقاس من إطار الأصل نفسه (الذي يُستبدل) لكل قناة
    عاملُ الإعتام k ونسبةُ بقاء المحتوى c، فيُبنى الإطار الجديد بهما من حالة المقطع الأخيرة."""
    def __init__(self, path, t_start, video, t_fade, t_end):
        super().__init__(path, t_start)
        self.nf = int(round(t_fade * 30)) - 2
        self.state = None; self.S0 = None
        flat = np.abs(PL - np.array([228, 236, 240], np.float32)).max(2) <= 1
        self.flat = flat

    def get(self, n, f):
        if n < self.nf: return super().get(n, f)
        ff = f.astype(np.float32)
        if self.state is None:
            self.state = super().get(self.nf, f).astype(np.float32); self.S0 = ff
            d = self.S0 - PL; self.strong = np.abs(d).max(2) > 40; self.dd = d[self.strong]
        k = np.median(ff[self.flat] / np.maximum(PL[self.flat], 1), 0)            # لكل قناة
        x = ff[self.strong] / k - PL[self.strong]
        c = float(np.clip((x * self.dd).sum() / (self.dd * self.dd).sum(), 0, 1))
        g = (PL + c * (self.state - PL)) * k
        return np.clip(g + 0.5, 0, 255).astype(np.uint8)
