{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/25.11";
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
            pythonPackages = pkgs.python312.pkgs;
          in
            with pythonPackages; [
              pip

              matplotlib
              numpy
              mne
              scipy
              scipy-stubs
              pylsl
              pyqtgraph
              pyqt6
              pyside6

              pkgs.qt6.qtbase

              # mne-lsl
              # pkgs.basedpyright
              pkgs.ty
              pkgs.liblsl
              # Add whatever else you'd like here.

              black

              # pkgs.ruff
              # or
              # python.pkgs.ruff
            ];
        };
      }
    );
}
