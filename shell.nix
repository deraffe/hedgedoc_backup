let
  sources = import ./npins;
  pkgs = import sources.nixpkgs { };
  pre-commit = (import sources."git-hooks.nix").run {
    src = ./.;
    default_stages = [
      "pre-commit"
      "pre-push"
    ];
    hooks = {
      nixfmt-rfc-style.enable = true;
      shellcheck.enable = true;
    };
  };
  shellPackages = with pkgs; [
    just
    python3
    uv
  ];
in
pkgs.mkShell {
  inherit (pre-commit) shellHook;
  buildInputs = shellPackages ++ pre-commit.enabledPackages;
}
