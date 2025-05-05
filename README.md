# HedgeDoc Backup

Simple script to quickly backup [HedgeDoc](https://hedgedoc.org/) notes with
links to one another.

To use it, you can either install [`uv`](https://docs.astral.sh/uv/) and
optionally [`just`](https://just.systems/) directly, or use the automatic setup
with [`direnv`](https://direnv.net/) and [`nix`](https://nixos.org/download/).

When using the `nix` environment, don't forget to tell `uv` not to manage Python.

```sh
uv venv -p "<path/to/python>"
```
