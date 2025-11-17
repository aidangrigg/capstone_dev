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
        devShells.default = pkgs.mkShell rec {
          packages = with pkgs; [
            cmake
            ninja
            gcc
            bluez
            bluez.dev
            just
            clang-tools
            liblsl
            gdb
          ];
          buildInputs = [
          ];
        };
      });
}
