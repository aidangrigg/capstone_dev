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

          packages = let
            pyPkgs = pkgs.python312.pkgs;
          in
            with pkgs; [
              pyPkgs.pip
              pyPkgs.python-lsp-server

              pyPkgs.pylsl
              pyPkgs.matplotlib
              pyPkgs.numpy
              pyPkgs.mne

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
