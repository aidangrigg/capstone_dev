{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs { inherit system; };
      in {
        devShells.default = pkgs.mkShell {
          venvDir = ".venv";

          postShellHook = ''
            export LD_LIBRARY_PATH=${pkgs.liblsl}/lib:$LD_LIBRARY_PATH
          '';

          packages = with pkgs; [
            python312.pkgs.venvShellHook
            python312.pkgs.pip

            liblsl
            # Add whatever else you'd like here.
            # pkgs.basedpyright

            # pkgs.black or python.pkgs.black

            # pkgs.ruff
            # or
            # python.pkgs.ruff
          ];
        };
      }
    );
}
