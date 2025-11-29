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
            pythonPackages = pkgs.python312.pkgs;
            # mne-lsl =
            #   let
            #     pname = "mne-lsl";
            #     version = "1.11.0";
            #   in
            #     pythonPackages.buildPythonPackage {
            #       inherit pname version;
            #       src = pkgs.fetchPypi {
            #         inherit pname version;
            #         # sha256 = "sha256-ikAz9jGqoVEpob6MFNw6lj1/BL7Zev9kYJIBw5w0nN0=";
            #       };
            #       doCheck = false;
            #     };
          in
            with pythonPackages; [
              pip

              matplotlib
              numpy
              mne

              # mne-lsl
              pkgs.basedpyright
              pkgs.liblsl
              # Add whatever else you'd like here.

              # pkgs.black or python.pkgs.black

              # pkgs.ruff
              # or
              # python.pkgs.ruff
            ];
        };
      }
    );
}
