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
        devShells.default =
          let
            pythonVersion = pkgs.python312;
            pythonPackages = pythonVersion.pkgs;
            pyxdf = pythonPackages.buildPythonPackage rec {
              pname = "pyxdf";
              version = "1.17.4";

                pyproject = true;

                build-system = [
                  pythonPackages.hatchling
                  pythonPackages.hatch-vcs
                ];

              src = pythonPackages.fetchPypi{
                inherit version;
                inherit pname;
                sha256 = "sha256-N04+MGpSd9DuniSCrcsiEebgWXWP86/PVvORkkXa4qw=";
              };

              buildInputs = [ pythonPackages.numpy ];
            };
          in
          pkgs.mkShell {
          venvDir = ".venv";

          postShellHook = ''
            export LD_LIBRARY_PATH=${pkgs.liblsl}/lib:$LD_LIBRARY_PATH
          '';

          packages = with pythonPackages; [
              pip

              mne
              pyxdf

              matplotlib
              numpy
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
              pkgs.pyright
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
