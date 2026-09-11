#!/usr/bin/env python3
"""Local server for verifying the expo — WITH byte-range support.

`python3 -m http.server` answers every request with the whole file, so a
<video> cannot seek: a reel that must start mid-tape sits on frame 0 and the
projector shows a white slate. GitHub Pages answers ranges; so does this.

    python3 qa/serve.py            # http://localhost:8777/expo/expo.html
    python3 qa/serve.py 8080
"""
import os, re, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        # the repo root is the old research tool; the exhibition is what we verify
        if self.path in ('/', '/index.html'):
            self.send_response(302); self.send_header('Location', '/expo/expo.html')
            self.end_headers(); return None
        path = self.translate_path(self.path)
        if os.path.isdir(path) or 'Range' not in self.headers:
            return super().send_head()
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404, 'File not found'); return None
        size = os.fstat(f.fileno()).st_size
        m = re.match(r'bytes=(\d*)-(\d*)$', self.headers['Range'].strip())
        if not m:
            f.close(); return super().send_head()
        a, b = m.groups()
        start = int(a) if a else max(0, size - int(b))
        end = int(b) if (b and a) else size - 1
        end = min(end, size - 1)
        if start > end or start >= size:
            self.send_response(416); self.send_header('Content-Range', f'bytes */{size}')
            self.end_headers(); f.close(); return None
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        f.seek(start)
        self._range_len = end - start + 1
        return f

    def copyfile(self, src, dst):
        n = getattr(self, '_range_len', None)
        if n is None:
            return super().copyfile(src, dst)
        while n > 0:
            chunk = src.read(min(1 << 16, n))
            if not chunk: break
            dst.write(chunk); n -= len(chunk)

    def end_headers(self):
        if 'Range' not in self.headers:
            self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()

    def log_message(self, *a):
        pass

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    print(f'serving {os.getcwd()} on http://localhost:{port}/expo/expo.html (ranges on)')
    ThreadingHTTPServer(('', port), RangeHandler).serve_forever()
