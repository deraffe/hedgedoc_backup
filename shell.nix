let
  sources = import ./npins;
  pkgs = import sources.nixpkgs { };
in pkgs.mkShell { buildInputs = with pkgs; [ just python3 uv ]; }
