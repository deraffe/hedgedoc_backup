let
  sources = import ./npins;
  pkgs = import sources.nixpkgs { };
  pyright-wrapper = pkgs.writeShellScript "pyright-wrapper" ''
    ${pkgs.uv}/bin/uv run ${pkgs.pyright}/bin/pyright "$@"
  '';
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
      check-symlinks.enable = true;
      nixfmt-rfc-style.enable = true;
      editorconfig-checker.enable = true;
      commitizen = {
        enable = true;
        package = pkgs.commitizen;
      };
      markdownlint = {
        enable = true;
        excludes = [ "^CHANGELOG.md$" ];
      };
      typos.enable = true;
      reuse.enable = true;
      ruff.enable = true;
      ruff-format.enable = true;
      pyright = {
        enable = true;
        settings.binPath = "${pyright-wrapper}";
      };
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
