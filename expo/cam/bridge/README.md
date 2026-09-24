# Tapo C113 → the hall

The camera speaks RTSP, a browser does not. **go2rtc** (one small program, Mac
and Windows alike) sits on the hall's computer and hands the same picture to
the browser as WebRTC, without re-encoding it. Nothing leaves the computer.

```
Tapo C113 ──RTSP (Wi-Fi)──▶ go2rtc on 127.0.0.1:1984 ──WebRTC──▶ expo.html?cam=tapo
                                                          └─▶ visitor-cam.js: people, near, hands, smiles
```

## Once, in the Tapo app

1. The camera → ⚙ → **Advanced Settings → Camera Account** → set a login and
   password. This is the camera's own account, not the TP-Link one. No `@ : / # ?`
   in the password: it goes inside a URL.
2. The camera → ⚙ → **Device Info** → note the **IP address**. Better: give the
   camera a fixed address (DHCP reservation) on the show router.
3. The computer running the hall and the camera must be on the **same network**.

## On the computer

1. Copy `camera.env.example` to `camera.env` and fill in the three lines.
   `camera.env` is ignored by git; the password never enters the repo.
2. Start the bridge:
   - macOS: double-click `start-bridge.command` (or run it in Terminal)
   - Windows: double-click `start-bridge.bat`

   The first start downloads go2rtc v1.9.14 from GitHub into `bin/`.
3. Check: open <http://127.0.0.1:1984> — the go2rtc page lists `tapo` and
   `tapo_sd`; the "stream" link plays the camera.
4. Open the hall with **`?cam=tapo&camdbg`**. The debug window at the bottom
   right shows what the model sees. The address is remembered on that machine,
   so later a plain `expo.html` has the camera too; `?cam=off` forgets it.

## Addresses

| | |
|---|---|
| `?cam=tapo` | the camera, 2K stream |
| `?cam=tapo:tapo_sd` | the camera, 640×360 stream (lighter) |
| `?cam=webcam` | this computer's own camera (developing on the Mac) |
| `?cam=file:media/patel_01.mp4` | a video file instead of a camera (testing) |
| `?camdbg` | the debug window |
| `?camnear=0.10` | where "near" begins: shoulder width as a fraction of the frame |
| `?camstats=csv` | download the daily visitor counter from this machine |
| `?cam=off` | turn the camera off and forget it |

## What the hall does with it

- A person who comes **near** wakes the hall from the tour, like a touch.
  Only a new arrival wakes it, so someone standing at the stand all day does not.
- While someone is near, the idle clock runs at quarter speed, as over an open page.
- Nobody near for 12 s → the tour resumes (it used to wait 45 s).
- Counter, per day: visitors, those who came near, minutes near the screen,
  most people at once, busiest hour, which reading pages were opened. Numbers
  only. No frame is stored or sent anywhere.

## If Chrome asks about "local network access"

The hall on GitHub Pages is a public site asking `127.0.0.1`, so newer Chrome
asks once. Allow it. Or run the hall locally on the show machine.
