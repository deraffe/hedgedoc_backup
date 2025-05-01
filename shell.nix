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
      check-case-conflicts.enable = true;
      check-executables-have-shebangs.enable = true;
      check-shebang-scripts-are-executable.enable = true;
      trim-trailing-whitespace.enable = true;
      nixfmt-rfc-style.enable = true;
      editorconfig-checker.enable = true;
      commitizen.enable = true;
      markdownlint.enable = true;
      ruff.enable = true;
      ruff-format.enable = true;
      pyright.enable = true;
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
