{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05";
    tau.url = "github:tau-lang/tau";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { nixpkgs, tau, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        lib = nixpkgs.lib;
        bi = [
          tau.packages."${system}".default
          pkgs.gcc
          pkgs.python313
        ];
      in {
        packages = rec {
          default = ochtendzon;

          ochtendzon = pkgs.python313.pkgs.buildPythonPackage {
            pname = "ochtendzon";
            version = "0.1.0";

            src = ./.; 
            format = "pyproject";
            
            nativeBuildInputs = [
              pkgs.python313Packages.uv-build
            ];

            buildInputs = bi;

            propagatedBuildInputs = [ pkgs.python313Packages.toml ];

            meta = {
              homepage = "https://github.com/tau-lang/ochtendzon";
              license = lib.licenses.eupl12;
              platforms = lib.platforms.all;
            };
          };

          ochtendzon-manpages = pkgs.stdenv.mkDerivation {
            pname = "ochtendzon-manpages";
            version = "0.1.0";

            src = ./.;

            installPhase = ''
              mkdir -p $out/share/man/man1
              cp man/ochtendzon.1 $out/share/man/man1/
            '';

            meta = {
              homepage = "https://github.com/tau-lang/ochtendzon";
              license = lib.licenses.eupl12;
              platforms = lib.platforms.all;
            };
          };
        };
        devShells.default =
          pkgs.mkShell { 
            buildInputs = bi ++ [ pkgs.nixfmt pkgs.uv ];

            env = {
              UV_NO_SYNC = "1";
              UV_PYTHON = "${pkgs.python313}/bin/python";
              UV_PYTHON_DOWNLOADS = "never";
            };

            shellHook = ''
              unset PYTHONPATH
            '';  
          };
      });
}
