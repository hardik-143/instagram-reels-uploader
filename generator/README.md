# What-if Reel generator

Code that renders the @whatif.wala Reels: flat cartoon characters, speech bubbles with typewriter text, word-by-word captions, a time badge, synthesized music and sound effects. Output is a 1080×1920, 30 fps H.264 MP4 with AAC audio.

Requirements: Python 3 with Pillow and NumPy, `ffmpeg` on the PATH, and the Poppins + Inter fonts under `/usr/share/fonts`.

## Making a video

Each video is one small script, `vid_<topic>.py`, that builds a config and calls `engine.main(cfg, "<output_name>")`. Run it from this folder:

```bash
cd generator
python3 vid_day100.py preview 2.5,8,16,24   # contact sheet: <output_name>_preview.png
python3 vid_day100.py                       # renders <output_name>.mp4 (~2 s of render per 1 s of video)
```

Copy the closest existing `vid_*.py` and edit it. `vid_day100.py` (10 scenes, ~88 s) and `vid_gravity.py` (custom floating props) are good starting points.

## Config reference

`cfg` keys:

- `total`: video length in seconds.
- `scenes`: list of scene dicts, in time order. The first has `id="intro"`, the last `id="outro"`.
- `intro`: `{"lines": [(sprite, y, start_time, "pop" | "left" | "right"), ...], "extra": fn(frame, draw, T)}`. Build title sprites with `engine.title([(text, colour), ...], size)`.
- `outro`: `{"lines": [(sprite, y, start_offset), ...], "row": [(char_kind, state), ...], "note": optional sprite}`.
- `music`: list of `dict(t0, t1, drums=True, clap=True, minor=False, melody=False, g=1.0)`. End the music at `twist_scene.s - 0.15` so the twist plays in silence.
- `drones`: optional list of `dict(t0, dur, g)` for an ambient drone.
- `fx`: list of `(sfx_name, time, gain[, kwargs])`. Add your own with `@engine.sfx` on a function that returns a NumPy array at 44.1 kHz.

Scene keys:

- `id`, `s`, `e`: name, start and end time.
- `bg`: background name, or `bg_fn(T)` returning an RGBA image.
- `clock`: text for the time badge, or `fn(T)` for a live counter.
- `char`: character kind. `pos` is `(cx, cy, size)` or `fn(T)`; the default is `(540, 1080, 600)`. Optional: `state`, `rot`, `look=(x, y)`, `enter`.
- `say`, `say_at`, `pitch`: speech-bubble text (UPPERCASE words turn red), when typing starts, and babble pitch in Hz.
- `narr`, `n_at`, `narr_y`: caption text (UPPERCASE words and numbers turn yellow), start time, and centre y (default 1470).
- `props(frame, draw, T, scene)`: drawn behind the character. `props_after`: drawn in front of it. `overlay(frame, T, scene)`: returns a new frame, for flashes and fades.
- `twist=True`: adds a record scratch before the scene and a ding after the line.

Sounds added automatically: a boom and pops in the intro, a whoosh at each scene change, a tick for each time badge, babble for speech bubbles, a pop when a character enters, and the outro pops and ding.

## Library

Characters: `dog cat cow pigeon mosquito sun flower penguin fish worm earth bat hockey football cloud heart whale uncle kid samosa trex trike diya ladoo moon auto train rocket chai`. Special states: `uncle` takes `"angry"` or `"hat"`, `kid` takes `"puff"`, `sun` takes `0` (switched off), `earth` takes a spin offset, and the reel animals take `"wink"`.

Backgrounds: `intro outro dog cat cow pigeon mosquito twist space day night week year deep sea1721 stadium gully living speed storm ocean pole pool sea cinema diwali sweetshop smog train cretaceous digsite office hot bedroom`. Add new ones in `engine.build_bg`.

Sound effects: `whoosh boom pop tick click powerdown scratch ding crash screech rumble wind gale waves splash underwater bubbles gasp heartbeat crowd cheer whistle seagulls kwak`.

## Layout rules

The time badge sits at y≈228–312. Speech bubbles end at y≈800. Characters default to centre (540, 1080). Captions are centred on y=1470 and fit 2–3 lines, so keep `narr` to about 12 words. Keep anything important clear of the bottom 300 px and the right edge, where Instagram's buttons sit.
